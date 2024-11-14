from flask import jsonify, request
from models import CommonJob, JobStatus, db
from flask import Blueprint
from datetime import datetime
from webview import FOLDER_DIALOG
import os

common_job_bp = Blueprint("common_job", __name__)


@common_job_bp.route("/job-add/", methods=["POST"])
def add_common_job():
    params = request.json.get("params", {})
    user_id = request.json.get("user_id", "")
    params["user_id"] = user_id
    job_type = request.json.get("job_type", "")
    if not job_type:
        job_type = params.get("job_type", "")
    if not job_type:
        return jsonify({"msg": "job_type is required", "code": 400})

    job = CommonJob(
        params=params,
        status=JobStatus.QUEUED,
        user_id=user_id,
        job_type=job_type,
        result={},
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(
        {
            "msg": "ok",
            "code": 200,
            "id": job.id,
            "data": {
                "id": job.id,
                "job_type": job_type,
                "params": params,
                "status": job.status,
                "result": {},
            },
        }
    )


@common_job_bp.route("/job-status/", methods=["GET"])
def get_status():
    _id = request.args.get("id")
    if _id:
        instance = CommonJob.query.get(_id)
        if instance:
            return jsonify(
                {
                    "msg": "ok",
                    "code": 200,
                    "status": instance.status,
                    "result": instance.result,
                    "params": instance.params,
                }
            )
        else:
            return jsonify({"msg": "id is not exist: ID " + str(_id), "code": 400})
    else:
        return jsonify({"msg": "id is required", "code": 400})


@common_job_bp.route("/job-delete/", methods=["DELETE"])
def delete():
    id = request.args.get("id")
    if id:
        instance = CommonJob.query.get(id)
        db.session.delete(instance)
        db.session.commit()
    return jsonify({"msg": "ok", "code": 200})


@common_job_bp.route("/job-update/", methods=["PUT"])
def update():
    id = request.json.get("id")
    status = request.json.get("status")
    params = request.json.get("params")
    if id and status:
        instance = CommonJob.query.get(id)
        instance.status = status
        instance.params = params
        db.session.commit()
    return jsonify({"msg": "ok", "code": 200})


@common_job_bp.route("/job-get/", methods=["GET"])
def get_job():
    id = request.args.get("id")
    if id:
        instance = CommonJob.query.get(id)
        return jsonify(
            {
                "msg": "ok",
                "code": 200,
                "data": {
                    "id": instance.id,
                    "job_type": instance.job_type,
                    "status": instance.status,
                    "result": instance.result,
                    "params": instance.params,
                },
            }
        )
    else:
        return jsonify({"msg": "id is required", "code": 400})
