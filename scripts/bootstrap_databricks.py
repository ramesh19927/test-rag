"""Bootstrap script for Databricks deployments."""
from app.databricks import delta_tables, vector_search, workspace_utils
from app.databricks.mlflow_tracking import configure_experiment


def main() -> None:
    """Provision workspace assets such as Unity Catalog schema and Vector Search index."""
    client = workspace_utils.get_workspace_client()
    configure_experiment()
    delta_tables.ensure_all_tables()
    vector_search.ensure_vector_index()
    print("Databricks bootstrap complete")


if __name__ == "__main__":
    main()
