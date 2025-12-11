def detect_request_type(req_text: str) -> str:
    text = req_text.casefold()

    TYPES = {
        "Bug Report": ["버그","장애", "고장", "안됨", "error", "Error", "bug", "issue", "exception" "fail", "broken"],
        "Data Request": ["데이터","로그", "데이터셋", "수집", "data", "Data", "log", "collector", "Collector", "dataset", "Dataset"],
        "Console UI / Control": ["조작", "화면", "제어", "마스터암", "팔", "ui", "UI", "ux", "console", "Console", "control", "Control", "dashboard", "arm", "Arm"],
        "Model / AI Request": ["모델", "추론", "학습", "model", "inference", "on-device", "ai", "onnx", "tensorrt"],
        "Habilis / Architecture": ["하빌리스", "알고리즘", "habillis", "habilis", "trajectory", "planner", "brain"],
        "Field Request / Deployment": ["필드", "현장", "현장 테스트", "deploy", "deployment"],
        "Enhancement / Feature Request": ["개선", "개발", "추가", "기능", "업데이트", "enhancement"],
    }

    for req_type, keywords in TYPES.items():
        if any(k in text for k in keywords):
            return req_type

    return "# General Inquiry"