import argparse
import csv
import os

from sklearn.metrics import precision_score, recall_score

from resume_parser import extract_text_from_path
from nlp_utils import preprocess_text
from matcher import rank_resumes


def load_labels(path):
    labels = {}
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            labels[row["filename"]] = int(row["label"])
    return labels


def main():
    parser = argparse.ArgumentParser(description="Evaluate resume matching precision/recall")
    parser.add_argument("--job", required=True, help="Path to job description text file")
    parser.add_argument("--resumes", required=True, help="Folder containing resume files")
    parser.add_argument("--labels", required=True, help="CSV with filename,label columns")
    parser.add_argument("--method", default="tfidf", choices=["tfidf", "semantic"])
    parser.add_argument("--threshold", type=float, default=70)
    args = parser.parse_args()

    with open(args.job, "r", encoding="utf-8") as handle:
        job_description = handle.read()

    labels = load_labels(args.labels)

    resume_files = [
        f
        for f in os.listdir(args.resumes)
        if f.lower().endswith((".pdf", ".docx"))
    ]

    resume_texts = []
    filenames = []

    for filename in resume_files:
        path = os.path.join(args.resumes, filename)
        resume_texts.append(extract_text_from_path(path))
        filenames.append(filename)

    job_clean = preprocess_text(job_description)
    resume_clean = [preprocess_text(text) for text in resume_texts]

    scores = rank_resumes(resume_clean, job_clean, args.method)

    y_true = []
    y_pred = []

    for idx, filename in enumerate(filenames):
        if filename not in labels:
            continue
        y_true.append(labels[filename])
        y_pred.append(1 if scores[idx] >= args.threshold else 0)

    if not y_true:
        raise SystemExit("No labeled resumes matched the input set.")

    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)

    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")


if __name__ == "__main__":
    main()
