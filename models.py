from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, BINARY, Integer, DateTime, JSON

db = SQLAlchemy()

from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    SPLIT_QUEUED = "split_queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    HOLD = "hold"


class Video(db.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(4096), index=True)  # 文件路径
    modify_time = Column(DateTime)  # 文件修改时间


class SubtitleSummary(db.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(4096), index=True)  # 文件路径
    params = Column(JSON, default={})
    status = Column(String, default=JobStatus.QUEUED)  # 梗概生成状态
    result = Column(JSON, default={})
    start_time = Column(DateTime)  # 开始时间

    def get_or_create(self):
        instance = db.session.query(SubtitleSummary).filter_by(path=self.path).first()
        if instance:
            return instance
        else:
            db.session.add(self)
            db.session.commit()
            return instance


class SubtitleTranslate(db.Model):
    id = Column(Integer, primary_key=True)
    path = Column(String(4096), index=True)  # 文件路径
    params = Column(JSON, default={})
    status = Column(String, default=JobStatus.QUEUED)  # 梗概生成状态
    result = Column(JSON, default={})
    start_time = Column(DateTime)  # 开始时间

    def get_or_create(self):
        instance = db.session.query(SubtitleTranslate).filter_by(path=self.path).first()
        if instance:
            return instance
        else:
            db.session.add(self)
            db.session.commit()
            return instance


class SubtitleClear(db.Model):
    id = Column(Integer, primary_key=True)
    input_path = Column(String(4096), index=True)  # 文件路径
    params = Column(JSON, default={})
    output_path = Column(String(4096), index=True)  # 文件路径
    result = Column(JSON, default={})
    start_time = Column(DateTime)  # 开始时间
    status = Column(String, default=JobStatus.QUEUED)  # 梗概生成状态

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self


class CommonJob(db.Model):
    id = Column(Integer, primary_key=True)
    job_type = Column(String(64), index=True)  # 任务类型
    status = Column(String, default=JobStatus.QUEUED)  # 任务状态
    result = Column(JSON, default={})  # 任务结果
    params = Column(JSON, default={})  # 任务参数
    start_at = Column(DateTime)  # 开始时间
    end_at = Column(DateTime)  # 结束时间
    user_id = Column(String(64), index=True)  # 用户ID

    def get_or_create(self):
        instance = (
            db.session.query(CommonJob)
            .filter_by(job_type=self.job_type, user_id=self.user_id)
            .first()
        )
        if instance:
            return instance
        else:
            db.session.add(self)
            db.session.commit()
            return instance
