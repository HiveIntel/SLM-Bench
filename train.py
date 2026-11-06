import argparse
import numpy as np
from datasets import ClassLabel, Sequence, load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    TrainingArguments,
    Trainer,
)
import smtplib
from email.mime.text import MIMEText
import datetime
import json
import math
import os
import logging
import traceback
from typing import Callable, Dict, List, Optional, Tuple
import torch
import gc
from time import sleep

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("experiments.log"), logging.StreamHandler()],
)
# Hugging Face downloads log every HTTP request at INFO; keep only problems
# (huggingface_hub uses httpx, or httpx2 in newer releases)
for http_logger in ("httpx", "httpx2"):
    logging.getLogger(http_logger).setLevel(logging.WARNING)

LETTERS = "ABCDEFGHIJ"

# A formatter turns one raw dataset row into zero or more (prompt, answer) pairs.
# The model is fine-tuned to produce `answer` after `prompt`; loss and metrics
# only count answer tokens.
Pair = Tuple[str, str]
Formatter = Callable[[Dict, Dict], List[Pair]]


def _multiple_choice(stem: str, options: List[str], answer_idx: int) -> List[Pair]:
    lines = [stem] + [f"{LETTERS[i]}. {opt}" for i, opt in enumerate(options)]
    lines.append("Answer:")
    return [("\n".join(lines), f" {LETTERS[answer_idx]}")]


def _entities(tokens: List[str], tags: List[str]) -> str:
    # Collapse BIO/IOB tags into "TYPE: span" items
    spans, current_type, current = [], None, []
    for token, tag in zip(tokens, tags):
        if tag == "O":
            prefix, ent_type = "O", None
        else:
            prefix, ent_type = tag.split("-", 1)
        if ent_type is None or prefix == "B" or ent_type != current_type:
            if current:
                spans.append(f"{current_type}: {' '.join(current)}")
            current_type, current = ent_type, []
        if ent_type is not None:
            current.append(token)
    if current:
        spans.append(f"{current_type}: {' '.join(current)}")
    return "; ".join(spans) if spans else "none"


def _label_names(features, field: str) -> List[str]:
    feature = features[field]
    if isinstance(feature, Sequence):
        feature = feature.feature
    if isinstance(feature, list):
        feature = feature[0]
    if not isinstance(feature, ClassLabel):
        raise ValueError(f"Field '{field}' has no class names")
    return feature.names


def fmt_boolq(row, info):
    prompt = f"{row['passage']}\nQuestion: {row['question']}?\nAnswer:"
    return [(prompt, " yes" if row["answer"] else " no")]


def fmt_arc(row, info):
    labels = row["choices"]["label"]
    if row["answerKey"] not in labels:
        return []
    return _multiple_choice(
        f"Question: {row['question']}",
        row["choices"]["text"],
        labels.index(row["answerKey"]),
    )


def fmt_openbookqa(row, info):
    labels = row["choices"]["label"]
    return _multiple_choice(
        f"Question: {row['question_stem']}",
        row["choices"]["text"],
        labels.index(row["answerKey"]),
    )


def fmt_piqa(row, info):
    return _multiple_choice(
        f"Goal: {row['goal']}\nWhich solution is better?",
        [row["sol1"], row["sol2"]],
        int(row["label"]),
    )


def fmt_hellaswag(row, info):
    if row["label"] == "":
        return []
    return _multiple_choice(
        f"Context: {row['ctx']}\nWhich ending is most plausible?",
        row["endings"],
        int(row["label"]),
    )


def fmt_winogrande(row, info):
    if row["answer"] == "":
        return []
    return _multiple_choice(
        f"Fill in the blank: {row['sentence']}",
        [row["option1"], row["option2"]],
        int(row["answer"]) - 1,
    )


def fmt_gsm8k(row, info):
    return [(f"Question: {row['question']}\nAnswer:", f" {row['answer']}")]


def fmt_aqua(row, info):
    options = [opt.split(")", 1)[1] if ")" in opt else opt for opt in row["options"]]
    return _multiple_choice(
        f"Question: {row['question']}", options, LETTERS.index(row["correct"])
    )


def fmt_race(row, info):
    return _multiple_choice(
        f"{row['article']}\nQuestion: {row['question']}",
        row["options"],
        LETTERS.index(row["answer"]),
    )


def fmt_coqa(row, info):
    # One example per conversation turn, with earlier turns as history
    pairs, history = [], ""
    for question, answer in zip(row["questions"], row["answers"]["input_text"]):
        pairs.append((f"{row['story']}\n{history}Q: {question}\nA:", f" {answer}"))
        history += f"Q: {question}\nA: {answer}\n"
    return pairs


def fmt_data_to_text(row, info):
    return [
        (
            f"Meaning representation: {row['meaning_representation']}\nDescription:",
            f" {row['target']}",
        )
    ]


def fmt_qnli(row, info):
    prompt = (
        f"Question: {row['question']}\nSentence: {row['sentence']}\n"
        "Does the sentence answer the question?\nAnswer:"
    )
    return [(prompt, " yes" if row["label"] == 0 else " no")]


def fmt_ner_tags(row, info):
    tags = [info["tag_names"][t] for t in row["tags"]]
    prompt = f"Sentence: {' '.join(row['tokens'])}\nEntities:"
    return [(prompt, f" {_entities(row['tokens'], tags)}")]


def fmt_conll(row, info):
    # Raw CoNLL block: one "token POS chunk NER" line per token
    lines = [line.split() for line in row["text"].strip().splitlines() if line.strip()]
    if not lines or lines[0][0] == "-DOCSTART-":
        return []
    tokens, tags = [l[0] for l in lines], [l[-1] for l in lines]
    prompt = f"Sentence: {' '.join(tokens)}\nEntities:"
    return [(prompt, f" {_entities(tokens, tags)}")]


def fmt_classification(row, info):
    label = _label_names(info["features"], "label")[row["label"]]
    return [(f"Text: {row['text']}\nCategory:", f" {label}")]


def fmt_reuters(row, info):
    if not row["topics"]:
        return []
    names = _label_names(info["features"], "topics")
    topics = ", ".join(names[t] for t in row["topics"])
    return [(f"{row['title']}\n{row['body']}\nTopics:", f" {topics}")]


def fmt_covid(row, info):
    if not row["prediction"]:
        return []
    return [(f"Tweet: {row['text']}\nSentiment:", f" {row['prediction'][0]['label']}")]


def fmt_drop(row, info):
    # Validation rows repeat the same span once per annotator
    spans = list(dict.fromkeys(row["answers_spans"]["spans"]))
    if not spans:
        return []
    prompt = f"{row['passage']}\nQuestion: {row['question']}\nAnswer:"
    return [(prompt, f" {', '.join(spans)}")]


FORMATTERS: Dict[str, Formatter] = {
    "boolq": fmt_boolq,
    "arc": fmt_arc,
    "openbookqa": fmt_openbookqa,
    "piqa": fmt_piqa,
    "hellaswag": fmt_hellaswag,
    "winogrande": fmt_winogrande,
    "gsm8k": fmt_gsm8k,
    "aqua": fmt_aqua,
    "race": fmt_race,
    "coqa": fmt_coqa,
    "data_to_text": fmt_data_to_text,
    "qnli": fmt_qnli,
    "ner_tags": fmt_ner_tags,
    "conll": fmt_conll,
    "classification": fmt_classification,
    "reuters": fmt_reuters,
    "covid": fmt_covid,
    "drop": fmt_drop,
}


class ExperimentManager:
    def __init__(
        self,
        email: Optional[str] = None,
        train_samples: int = 100,
        eval_samples: int = 50,
        max_length: int = 512,
        batch_size: int = 4,
        epochs: float = 1.0,
        seed: int = 42,
    ):
        self.email = email
        self.train_samples = train_samples
        self.eval_samples = eval_samples
        self.max_length = max_length
        self.batch_size = batch_size
        self.epochs = epochs
        self.seed = seed
        self.results_dir = "experiment_results"
        os.makedirs(self.results_dir, exist_ok=True)
        self.failed_experiments = []
        self.successful_experiments = []

        # Load experiment configurations
        self.load_configurations()

    def load_configurations(self):
        # Load models and datasets from JSON files
        with open("models.json", "r") as f:
            self.models = json.load(f)["models"]
        with open("datasets.json", "r") as f:
            self.datasets = json.load(f)["datasets"]

    def select(self, models: Optional[List[str]], datasets: Optional[List[str]]):
        # Restrict the run to the named models/datasets (case-insensitive)
        def pick(entries, names, kind):
            if not names:
                return entries
            by_name = {e["name"].lower(): e for e in entries}
            unknown = [n for n in names if n.lower() not in by_name]
            if unknown:
                available = ", ".join(e["name"] for e in entries)
                raise SystemExit(f"Unknown {kind}: {', '.join(unknown)}. Available: {available}")
            return [by_name[n.lower()] for n in names]

        self.models = pick(self.models, models, "model(s)")
        self.datasets = pick(self.datasets, datasets, "dataset(s)")

    def cleanup_gpu(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        sleep(5)  # Give system time to free resources

    def send_email(self, subject: str, content: str):
        # Email notifications are opt-in: they need --email plus SMTP credentials
        # supplied through the environment (never hardcode them here).
        if not self.email:
            return

        smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        sender_email = os.environ.get("SMTP_USER")
        sender_password = os.environ.get("SMTP_PASSWORD")

        if not sender_email or not sender_password:
            logging.warning(
                "Skipping email: set SMTP_USER and SMTP_PASSWORD to enable notifications"
            )
            return

        msg = MIMEText(content)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = self.email

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            logging.info("Email sent successfully")
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")

    def load_split(self, dataset_info: Dict, split: str):
        source = dataset_info["source"]
        kwargs = dict(source.get("kwargs", {}))
        if "data_files" in source:
            kwargs["data_files"] = source["data_files"]
        return load_dataset(source["path"], source.get("config"), split=split, **kwargs)

    def encode_pair(self, prompt: str, answer: str, tokenizer) -> Optional[Dict]:
        # Tokenize prompt+answer together (so the boundary tokenizes naturally),
        # then mask everything before the answer out of the loss.
        encoded = tokenizer(prompt + answer, return_offsets_mapping=True)
        input_ids = list(encoded["input_ids"])
        offsets = encoded["offset_mapping"]
        answer_start = next(
            (i for i, (start, end) in enumerate(offsets) if end > start and end > len(prompt)),
            None,
        )
        if answer_start is None:
            return None

        prompt_ids = input_ids[:answer_start]
        answer_ids = input_ids[answer_start:] + [tokenizer.eos_token_id]

        # Keep the whole answer when possible; trim the prompt from the left
        # (keeping BOS) so the question right before the answer survives.
        answer_ids = answer_ids[: self.max_length * 3 // 4]
        room = self.max_length - len(answer_ids)
        if len(prompt_ids) > room:
            bos = tokenizer.bos_token_id
            if bos is not None and prompt_ids and prompt_ids[0] == bos:
                prompt_ids = [bos] + prompt_ids[len(prompt_ids) - room + 1 :]
            else:
                prompt_ids = prompt_ids[len(prompt_ids) - room :]

        return {
            "input_ids": prompt_ids + answer_ids,
            "attention_mask": [1] * (len(prompt_ids) + len(answer_ids)),
            "labels": [-100] * len(prompt_ids) + answer_ids,
        }

    def prepare_split(self, dataset, dataset_info: Dict, tokenizer, n_samples: int):
        formatter = FORMATTERS[dataset_info["format"]]
        info = {"features": dataset.features, **dataset_info["source"]}

        def encode_batch(batch):
            out = {"input_ids": [], "attention_mask": [], "labels": []}
            rows = [dict(zip(batch, values)) for values in zip(*batch.values())]
            for row in rows:
                for prompt, answer in formatter(row, info):
                    encoded = self.encode_pair(prompt, answer, tokenizer)
                    if encoded:
                        for key in out:
                            out[key].append(encoded[key])
            return out

        # Oversample raw rows because formatters may drop rows (no label) or
        # expand them (CoQA turns), then cap at n_samples encoded examples.
        raw = dataset.shuffle(seed=self.seed)
        raw = raw.select(range(min(len(raw), n_samples * 4)))
        encoded = raw.map(encode_batch, batched=True, remove_columns=raw.column_names)
        if len(encoded) == 0:
            raise ValueError(f"No usable examples in {dataset_info['name']}")
        return encoded.select(range(min(len(encoded), n_samples)))

    @staticmethod
    def preprocess_logits_for_metrics(logits, labels):
        if isinstance(logits, tuple):
            logits = logits[0]
        return logits.argmax(dim=-1)

    def compute_metrics(self, eval_preds):
        predictions, labels = eval_preds
        # Logits at position t predict token t+1
        predictions, labels = predictions[:, :-1], labels[:, 1:]
        mask = labels != -100
        correct = (predictions == labels) & mask
        per_example = correct.sum(axis=1) == mask.sum(axis=1)
        has_answer = mask.sum(axis=1) > 0
        return {
            # Fraction of answer tokens predicted correctly (teacher forcing)
            "token_accuracy": float(correct.sum() / max(mask.sum(), 1)),
            # Every answer token (incl. EOS) correct; equals greedy-decoding exact match
            "exact_match": float(per_example[has_answer].mean()) if has_answer.any() else 0.0,
        }

    def run_single_experiment(self, model_info: Dict, dataset_info: Dict) -> bool:
        experiment_name = f"{model_info['name']}_{dataset_info['name']}"
        logging.info(f"Starting experiment: {experiment_name}")
        model = trainer = None

        try:
            # Load dataset
            train_split = self.load_split(dataset_info, dataset_info["source"]["train_split"])
            eval_split = self.load_split(dataset_info, dataset_info["source"]["eval_split"])

            # Load model and tokenizer
            model_id = (
                model_info["huggingface_url"].split("/")[-2]
                + "/"
                + model_info["huggingface_url"].split("/")[-1]
            )
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "right"

            # Preprocess datasets
            tokenized_train = self.prepare_split(
                train_split, dataset_info, tokenizer, self.train_samples
            )
            tokenized_val = self.prepare_split(
                eval_split, dataset_info, tokenizer, self.eval_samples
            )

            # FP32 master weights with BF16/FP16 autocast where the GPU supports it
            model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
            model.config.pad_token_id = tokenizer.pad_token_id
            use_cuda = torch.cuda.is_available()
            use_bf16 = use_cuda and torch.cuda.is_bf16_supported()
            if use_cuda:
                torch.cuda.reset_peak_memory_stats()

            # Training arguments
            training_args = TrainingArguments(
                output_dir=f"{self.results_dir}/{experiment_name}",
                eval_strategy="epoch",
                learning_rate=2e-5,
                per_device_train_batch_size=self.batch_size,
                per_device_eval_batch_size=self.batch_size,
                num_train_epochs=self.epochs,
                weight_decay=0.01,
                bf16=use_bf16,
                fp16=use_cuda and not use_bf16,
                logging_steps=10,
                save_strategy="no",  # Don't save checkpoints to save space
                report_to="none",
                seed=self.seed,
            )

            # Initialize trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_train,
                eval_dataset=tokenized_val,
                processing_class=tokenizer,
                data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True),
                compute_metrics=self.compute_metrics,
                preprocess_logits_for_metrics=self.preprocess_logits_for_metrics,
            )

            # Training
            train_results = trainer.train()
            eval_results = trainer.evaluate()
            eval_results["eval_perplexity"] = math.exp(min(eval_results["eval_loss"], 50))

            # Save results
            results = {
                "model": model_info["name"],
                "model_id": model_id,
                "dataset": dataset_info["name"],
                "train_examples": len(tokenized_train),
                "eval_examples": len(tokenized_val),
                "training_loss": float(train_results.training_loss),
                "train_metrics": train_results.metrics,
                "eval_results": eval_results,
                "peak_gpu_memory_gb": (
                    torch.cuda.max_memory_allocated() / 1e9 if use_cuda else None
                ),
                "timestamp": datetime.datetime.now().isoformat(),
            }

            with open(f"{self.results_dir}/{experiment_name}_results.json", "w") as f:
                json.dump(results, f, indent=2)

            logging.info(
                f"Finished {experiment_name}: eval_loss={eval_results['eval_loss']:.4f} "
                f"token_accuracy={eval_results['eval_token_accuracy']:.4f} "
                f"exact_match={eval_results['eval_exact_match']:.4f}"
            )
            self.successful_experiments.append(experiment_name)
            return True

        except Exception as e:
            error_msg = f"Error in experiment {experiment_name}: {str(e)}\n{traceback.format_exc()}"
            logging.error(error_msg)
            self.failed_experiments.append(
                {"experiment": experiment_name, "error": str(e)}
            )
            return False
        finally:
            # Drop references so the model's memory can actually be released
            del model, trainer
            self.cleanup_gpu()

    def run_all_experiments(self):
        total_experiments = len(self.models) * len(self.datasets)
        completed = 0
        start_time = datetime.datetime.now()

        for model in self.models:
            for dataset in self.datasets:
                completed += 1
                logging.info(f"Progress: {completed}/{total_experiments} experiments")

                self.run_single_experiment(model, dataset)

                if completed % 10 == 0:  # Send progress email every 10 experiments
                    self.send_progress_email(completed, total_experiments, start_time)

        self.send_final_report(start_time)
        logging.info(
            f"Done: {len(self.successful_experiments)} succeeded, "
            f"{len(self.failed_experiments)} failed"
        )

    def send_progress_email(
        self, completed: int, total: int, start_time: datetime.datetime
    ):
        current_time = datetime.datetime.now()
        elapsed_time = current_time - start_time
        avg_time_per_exp = elapsed_time / completed
        remaining_experiments = total - completed
        estimated_remaining_time = avg_time_per_exp * remaining_experiments

        content = f"""
        Progress Report

        Completed: {completed}/{total} experiments
        Success Rate: {len(self.successful_experiments)}/{completed}
        Failed Experiments: {len(self.failed_experiments)}

        Time Elapsed: {elapsed_time}
        Estimated Time Remaining: {estimated_remaining_time}
        """

        self.send_email("Experiment Progress Update", content)

    def send_final_report(self, start_time: datetime.datetime):
        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        total_experiments = max(len(self.models) * len(self.datasets), 1)

        content = f"""
        Final Experiment Report

        Total Experiments: {len(self.models) * len(self.datasets)}
        Successful Experiments: {len(self.successful_experiments)}
        Failed Experiments: {len(self.failed_experiments)}

        Total Time: {total_time}
        Average Time per Experiment: {total_time / total_experiments}

        Failed Experiments Details:
        {json.dumps(self.failed_experiments, indent=2)}
        """

        self.send_email("Experiment Final Report", content)


def main():
    parser = argparse.ArgumentParser(description="Run multiple fine-tuning experiments")
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Optional address for progress emails (requires SMTP_USER and SMTP_PASSWORD env vars)",
    )
    parser.add_argument(
        "--models", nargs="+", help="Model names from models.json (default: all)"
    )
    parser.add_argument(
        "--datasets", nargs="+", help="Dataset names from datasets.json (default: all)"
    )
    parser.add_argument("--train-samples", type=int, default=100)
    parser.add_argument("--eval-samples", type=int, default=50)
    parser.add_argument(
        "--max-length", type=int, default=512, help="Max tokens per example"
    )
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--gpu-memory-fraction",
        type=float,
        default=None,
        help="Cap this process's share of GPU memory (useful on shared GPUs)",
    )
    args = parser.parse_args()

    if args.gpu_memory_fraction and torch.cuda.is_available():
        torch.cuda.set_per_process_memory_fraction(args.gpu_memory_fraction)

    manager = ExperimentManager(
        email=args.email,
        train_samples=args.train_samples,
        eval_samples=args.eval_samples,
        max_length=args.max_length,
        batch_size=args.batch_size,
        epochs=args.epochs,
        seed=args.seed,
    )
    manager.select(args.models, args.datasets)
    manager.run_all_experiments()


if __name__ == "__main__":
    main()
