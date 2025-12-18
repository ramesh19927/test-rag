"""Bootstrap local environment for the RAG platform."""
from app.databricks import delta_tables, vector_search
from app.databricks.mlflow_tracking import configure_experiment


def main() -> None:
    """Create local parity artifacts such as FAISS file and MLflow experiment."""
    configure_experiment()
    delta_tables.ensure_all_tables()
    vector_search.ensure_vector_index()
    print("Local bootstrap complete")


if __name__ == "__main__":
    main()
