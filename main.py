from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

# A simple model describing the data expected when creating or updating a patient.
class Patient(BaseModel):
    id: str
    name: str
    city: str
    age: int
    gender: str
    height: float
    weight: float
    bmi: float
    verdict: str


# Doctor IDs are the keys in doctors.json, so the ID isn't repeated here.
class Doctor(BaseModel):
    name: str
    specialty: str
    city: str
    age: int
    gender: str


def load_data():
    with open("users.json", "r") as f:
        return json.load(f)


def save_data(data):
    with open("users.json", "w") as f:
        json.dump(data, f, indent=2)


def load_doctors():
    with open("doctors.json", "r") as f:
        return json.load(f)


def save_doctors(doctors):
    with open("doctors.json", "w") as f:
        json.dump(doctors, f, indent=2)


@app.get("/")
def hello():
    return {"message": "Management system"}


@app.get("/about")
def about():
    return {"message": "This is a management system"}


# READ: get every patient
@app.get("/patients")
def get_patients():
    return load_data()


# READ: get one patient by ID
@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    patients = load_data()
    for patient in patients:
        if patient["id"] == patient_id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")


# READ: get all doctors
@app.get("/doctors")
def get_doctors():
    return load_doctors()


# READ: get one doctor by its dictionary key
@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    doctors = load_doctors()
    if doctor_id not in doctors:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"id": doctor_id, **doctors[doctor_id]}


# CREATE: add a patient (list format: append a record)
@app.post("/patients")
def create_patient(patient: Patient):
    patients = load_data()

    for existing_patient in patients:
        if existing_patient["id"] == patient.id:
            raise HTTPException(status_code=400, detail="Patient ID already exists")

    patients.append(patient.model_dump())
    save_data(patients)
    return patient


# CREATE: add a doctor (object format: assign a value to the ID key)
@app.post("/doctors/{doctor_id}")
def create_doctor(doctor_id: str, doctor: Doctor):
    doctors = load_doctors()
    if doctor_id in doctors:
        raise HTTPException(status_code=400, detail="Doctor ID already exists")

    doctors[doctor_id] = doctor.model_dump()
    save_doctors(doctors)
    return {"id": doctor_id, **doctors[doctor_id]}


# UPDATE: replace a patient's details (list format: find its index)
@app.put("/patients/{patient_id}")
def update_patient(patient_id: str, updated_patient: Patient):
    patients = load_data()
    for index, patient in enumerate(patients):
        if patient["id"] == patient_id:
            # Keep the URL ID as the patient's ID.
            updated_data = updated_patient.model_dump()
            updated_data["id"] = patient_id
            patients[index] = updated_data
            save_data(patients)
            return updated_data
    raise HTTPException(status_code=404, detail="Patient not found")


# UPDATE: replace a doctor's details at its ID key
@app.put("/doctors/{doctor_id}")
def update_doctor(doctor_id: str, updated_doctor: Doctor):
    doctors = load_doctors()
    if doctor_id not in doctors:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctors[doctor_id] = updated_doctor.model_dump()
    save_doctors(doctors)
    return {"id": doctor_id, **doctors[doctor_id]}


# DELETE: remove a patient (list format: find its index, then pop)
@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: str):
    patients = load_data()
    for index, patient in enumerate(patients):
        if patient["id"] == patient_id:
            deleted_patient = patients.pop(index)
            save_data(patients)
            return {"message": "Patient deleted", "patient": deleted_patient}
    raise HTTPException(status_code=404, detail="Patient not found")


# DELETE: remove a doctor (object format: pop the ID key)
@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: str):
    doctors = load_doctors()
    if doctor_id not in doctors:
        raise HTTPException(status_code=404, detail="Doctor not found")

    deleted_doctor = doctors.pop(doctor_id)
    save_doctors(doctors)
    return {"message": "Doctor deleted", "doctor": {"id": doctor_id, **deleted_doctor}}

