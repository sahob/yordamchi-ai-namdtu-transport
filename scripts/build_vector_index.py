from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Bu script vector indeksni lokalda quradi.
os.environ["BUILD_VECTOR_INDEX_ON_STARTUP"] = "true"

from backend.knowledge import KnowledgeBase  # noqa: E402


def main() -> None:
    kb = KnowledgeBase()
    status = kb.vector_status()
    print("Chunks:", len(kb.chunks))
    print("Vector status:", status)
    if not status.get("available"):
        raise SystemExit("Vector indeks yaratilmadi. OPENAI_API_KEY va billing/creditni tekshiring.")
    print("Tayyor: .cache/vector_index.json yaratildi yoki yangilandi.")


if __name__ == "__main__":
    main()
