from agent.graph import graph

from datetime import datetime

import os


os.makedirs(
    "data",
    exist_ok=True
)


try:
    result = graph.invoke({})
except RuntimeError as error:
    print(f"\nGeneration stopped: {error}")
    raise SystemExit(1)


final_post = result["final_post"]


print("\n=== FINAL POST ===\n")
print(final_post)


timestamp = datetime.now().strftime(
    "%Y%m%d_%H%M%S"
)


filename = (
    f"data/post_{timestamp}.txt"
)


with open(
    filename,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        final_post
    )


# ---------- IMAGE SAVE ----------

if "image_bytes" in result:

    os.makedirs(
        "images",
        exist_ok=True
    )

    image = result[
        "image_bytes"
    ]


    image.save(
        "images/post_image.png"
    )


    print(
        "\nSaved image: images/post_image.png"
    )

else:

    print(
        "\nNo image generated."
    )
