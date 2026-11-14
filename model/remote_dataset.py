class RemoteDataset:
    def __init__(self, name, session_id, uploaded_by, records, dataset_id=None, uploaded_at=None):
        self.dataset_id = dataset_id
        self.name = name
        self.session_id = str(session_id)
        self.uploaded_by = uploaded_by
        self.records = records
        self.uploaded_at = uploaded_at

    @classmethod
    def from_document(cls, document):
        return cls(
            name=document["name"],
            session_id=document["session_id"],
            uploaded_by=document["uploaded_by"],
            records=document["records"],
            dataset_id=document["_id"],
            uploaded_at=document.get("uploaded_at"),
        )