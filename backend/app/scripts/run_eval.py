"""
Retrieval Evaluation Runner CLI
Runs the benchmark suite across BM25, Dense Semantic, and Hybrid RAG retrieval methods,
prints formatted metrics (MRR, Recall@K, Precision@K), and saves docs/retrieval_evaluation_results.json.
"""
import os

from app.retrieval.evaluator import run_and_save_evaluation


def get_project_root() -> str:
    # __file__ is in backend/app/scripts/run_eval.py
    # 4 levels up is sentinelops-ai project root
    cur = os.path.abspath(__file__)
    for _ in range(4):
        cur = os.path.dirname(cur)
    return cur

def main():
    root = get_project_root()
    knowledge_dir = os.path.join(root, "knowledge", "runbooks")
    output_path = os.path.join(root, "docs", "retrieval_evaluation_results.json")

    print("=================================================================")
    print("        SENTINELOPS AI - RAG RETRIEVAL EVALUATION BENCHMARK      ")
    print("=================================================================")
    print(f"Loading runbooks from: {knowledge_dir}")
    print(f"Saving evaluation results to: {output_path}")

    results = run_and_save_evaluation(knowledge_dir, output_path)

    print("\n-----------------------------------------------------------------")
    print(f"{'Method':<12} | {'MRR':<8} | {'Recall@1':<9} | {'Recall@3':<9} | {'Precision@1':<12}")
    print("-----------------------------------------------------------------")
    for method, metrics in results.items():
        mrr = metrics["mrr"]
        r1 = metrics["recall"]["recall@1"]
        r3 = metrics["recall"]["recall@3"]
        p1 = metrics["precision"]["precision@1"]
        print(f"{method:<12} | {mrr:<8.4f} | {r1:<9.4f} | {r3:<9.4f} | {p1:<12.4f}")
    print("-----------------------------------------------------------------")
    print("Detailed per-query breakdown saved to docs/retrieval_evaluation_results.json\n")

if __name__ == "__main__":
    main()
