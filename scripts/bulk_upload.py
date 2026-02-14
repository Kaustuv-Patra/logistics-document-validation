import os
import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"
PDF_DIR = os.path.abspath("data/pdf_corpus")

def create_document(document_id, shipment_id, document_type):
    payload = {
        "document_id": document_id,
        "shipment_id": shipment_id,
        "document_type": document_type
    }
    r = requests.post(f"{BASE_URL}/documents", json=payload)
    if r.status_code != 200:
        raise Exception(f"Document creation failed: {r.text}")


def upload_file(document_id, file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        r = requests.post(f"{BASE_URL}/documents/{document_id}/file", files=files)
    if r.status_code != 200:
        raise Exception(f"File upload failed: {r.text}")


def process_folder(folder, document_type):
    for filename in os.listdir(folder):
        if not filename.endswith(".pdf"):
            continue

        index = filename.split("_")[1].split(".")[0]
        shipment_id = f"SHIP-{3000 + int(index)}"

        document_id = str(uuid.uuid4())

        print(f"Processing {filename}")

        create_document(document_id, shipment_id, document_type)
        upload_file(document_id, os.path.join(folder, filename))


def main():
    bol_path = os.path.join(PDF_DIR, "bol")
    pod_path = os.path.join(PDF_DIR, "pod")

    process_folder(bol_path, "BOL")
    process_folder(pod_path, "POD")

    print("Bulk upload complete.")


if __name__ == "__main__":
    main()
