from data_visualiser import DataVisualiser
from data.dataset_repository import DatasetRepository


def main():
    visualiser = DataVisualiser()
    repository = DatasetRepository()

    file_path = input("Enter CSV file path: ").strip().strip('"')
    session_id = input("Enter DES session ID: ").strip()

    if not visualiser.load_csv(file_path):
        print("Failed to load CSV.")
        return

    records = visualiser.get_data()

    try:
        dataset_id = repository.upload_dataset(
            name="Remote CSV Test",
            session_id=session_id,
            uploaded_by="Luke",
            records=records,
        )

        print("Dataset uploaded successfully.")
        print(f"Dataset ID: {dataset_id}")

        dataset = repository.find_by_id(dataset_id, session_id)

        if dataset is None:
            print("Failed to retrieve dataset.")
            return

        print(f"Retrieved dataset: {dataset.name}")
        print(f"Records retrieved: {len(dataset.records)}")

    except (ValueError, Exception) as error:
        print(f"Upload failed: {error}")


if __name__ == "__main__":
    main()
