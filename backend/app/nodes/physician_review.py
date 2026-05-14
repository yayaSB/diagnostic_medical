from backend.app.state import MedicalState


class PhysicianReviewNode:
    def __call__(self, state: MedicalState) -> MedicalState:
        # Human-in-the-loop: this node marks the pause point
        # The API handles actual physician input via /consultation/{thread_id}/physician-review
        return state