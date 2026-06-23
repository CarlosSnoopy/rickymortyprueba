import io
import pandas as pd

def generar_csv_bytes(data: list) -> bytes:
    df = pd.DataFrame(data)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding="utf-8")
    return buffer.getvalue().encode("utf-8")