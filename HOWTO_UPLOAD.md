# How to Upload

This guide explains how to upload files to the Crewbot1501 repository.

## Prerequisites

- A GitHub account with access to the [Crewbot1501 repository](https://github.com/martin125470/Crewbot1501)
- [Git](https://git-scm.com/downloads) installed on your local machine (for command-line uploads)
- Or a modern web browser (for uploads via the GitHub web interface)

## Option 1: Upload via the GitHub Web Interface

1. Navigate to the [Crewbot1501 repository](https://github.com/martin125470/Crewbot1501) in your browser.
2. Click the **Add file** button near the top-right of the file list.
3. Select **Upload files** from the drop-down menu.
4. Drag and drop your files onto the page, or click **choose your files** to browse and select them.
5. Scroll down to the **Commit changes** section.
6. Enter a short, descriptive commit message (e.g. `Add my upload`).
7. Choose whether to commit directly to `main` or to create a new branch and open a pull request.
8. Click **Commit changes** (or **Propose changes** if using a new branch).

## Option 2: Upload via the Command Line (Git)

1. **Clone the repository** (skip if you already have a local copy):
   ```bash
   git clone https://github.com/martin125470/Crewbot1501.git
   cd Crewbot1501
   ```

2. **Copy your files** into the local repository folder.

3. **Stage the new files**:
   ```bash
   git add .
   ```

4. **Commit the changes**:
   ```bash
   git commit -m "Add my upload"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin main
   ```

## Tips

- Keep file names short and descriptive, using lowercase letters and hyphens (e.g. `my-document.pdf`).
- Avoid committing large binary files directly; consider using [Git LFS](https://git-lfs.github.com/) for files larger than 100 MB.
- If you are unsure about a change, create a new branch and open a pull request so others can review it before it is merged.

## Getting Help

If you run into any problems, open an [issue](https://github.com/martin125470/Crewbot1501/issues) in this repository and describe what went wrong.
