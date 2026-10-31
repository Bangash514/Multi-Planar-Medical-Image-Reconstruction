# Computer-Vision-Face-Verification

Face verification in Python with **dlib's 128-d ResNet face embeddings** on the public **LFW (Labeled Faces in the Wild)** dataset from Kaggle. The scripts answer two questions:

1. **Same person or not?** Pair evaluation (accuracy, ROC AUC, true accept rate at 1% false accept rate), with the threshold chosen on one group of people and tested on different people.
2. **Is this the target person?** A one-person check using public LFW photos of George W. Bush (default): half of his photos build a template, the other half and photos of other people are the test set.

> Status: learning and portfolio project on a public benchmark. Not for surveillance or for identifying real people. This is **not** Facebook's DeepFace model; it uses the dlib model through the `face_recognition` package.

## Results
TODO: run on the full dataset and paste the numbers from `results/metrics_*.txt` here.

| Check | Value |
|---|---|
| Pair verification accuracy (test people) | TODO |
| ROC AUC | TODO |
| TAR at FAR 1% | TODO |
| One-person check ROC AUC | TODO |

## Data
LFW is **not included**. Download it from Kaggle: [jessicali9530/lfw-dataset](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) (folder layout `Person_Name/Person_Name_0001.jpg`). The scripts find the person folders automatically, even when the download is nested.

## Run
```
pip install -r requirements.txt
python src/01_embed.py --data path/to/lfw        # slow step: saves results/embeddings.npz
python src/02_verify_pairs.py                    # pair verification, ROC and histogram
python src/03_one_person.py --person George_W_Bush
```
Run from the project root. The default limits (400 people, 12 images each) keep a CPU run short; raise `--max-people` and `--max-per-person` for more data. A Colab notebook (`Run_Face_Colab.ipynb`) runs all steps.

On Windows, `pip install dlib-bin` gives a prebuilt dlib (no compiler needed).

## Files
- `src/common.py` - dataset folder search, embedding, caching
- `src/01_embed.py` - compute embeddings
- `src/02_verify_pairs.py` - same / different person evaluation
- `src/03_one_person.py` - one-person template check

## Ethics and limits
- Public benchmark data only. Do not use this code on people's photos without their consent, and follow privacy law (GDPR, PIPL and others).
- LFW is a famous-people dataset with known biases (more men, more light-skinned people), so scores do not carry over to other groups.
- Some LFW images are not detected by the face detector; a centre box is used for them (the number is printed).

## Use and contact
If you use, adapt or contribute to this work, please credit the author and **contact or inform me by email: owaiskhan_bangash@yahoo.com**

## Author
BEN, Software Engineer. GitHub: [Bangash514](https://github.com/Bangash514)
