import imumocap
import imumocap.file

import ximu3s

# Load model
root, _ = imumocap.file.load_model("model.json")

# Connect to and configure IMUs
imus = ximu3s.setup([l.name for l in root.flatten() if l.name], False)
