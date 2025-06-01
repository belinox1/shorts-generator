from pydantic import BaseModel

# === MODEL DEFINITION ===
class Script(BaseModel):
    theme: str
    title: str
    hook: str
    body: str
    close: str

    @property
    def text(self):
        return f"{self.hook} {self.body} {self.close}"