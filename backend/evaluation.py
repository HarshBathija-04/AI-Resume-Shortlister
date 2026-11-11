import argparse
import csv
import os

from sklearn.metrics import precision_score, recall_score

from matcher import rank_resumes
from nlp_utils import preprocess_text
from resume_parser import extract_text_from_path


def load_labels(path):
    with open(path, encoding="utf-8") as handle:
        return {row["filename"]: int(row["label"]) for row in csv.DictReader(handle)}


def main():
    parser = argparse.ArgumentParser(description="Evaluate resume matching precision/recall")
    parser.add_argument("--job", required=True, help="Path to job description text file")
    parser.add_argument("--resumes", required=True, help="Folder containing resume files")
    parser.add_argument("--labels", required=True, help="CSV with filename,label columns")
    parser.add_argument("--method", default="tfidf", choices=["tfidf", "semantic"])
    parser.add_argument("--threshold", type=float, default=70)
    args = parser.parse_args()

    with open(args.job, encoding="utf-8") as handle:
        job_description = handle.read()

    labels = load_labels(args.labels)

    filenames = [f for f in os.listdir(args.resumes) if f.lower().endswith((".pdf", ".docx"))]
    resume_texts = [preprocess_text(extract_text_from_path(os.path.join(args.resumes, f))) for f in filenames]
    scores = rank_resumes(resume_texts, preprocess_text(job_description), args.method)

    labelled = [(f, score) for f, score in zip(filenames, scores, strict=True) if f in labels]
    y_true = [labels[f] for f, _ in labelled]
    y_pred = [int(score >= args.threshold) for _, score in labelled]

    if not y_true:
        raise SystemExit("No labeled resumes matched the input set.")

    print(f"Precision: {precision_score(y_true, y_pred):.3f}")
    print(f"Recall: {recall_score(y_true, y_pred):.3f}")


if __name__ == "__main__":
    main()
