#!/usr/bin/env python3
"""
=============================================================
File: backend/setup.py
Purpose: One-click setup script — installs all dependencies
         including the correct spaCy model version.

Usage:
    python setup.py

Works on: Windows, Mac, Linux
=============================================================
"""

import subprocess
import sys
import os

def run(cmd, description=""):
    """Run a shell command and print result."""
    print(f"\n{'='*55}")
    print(f"  {description or cmd}")
    print(f"{'='*55}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"  ⚠️  Warning: command exited with code {result.returncode}")
    return result.returncode == 0

def get_spacy_version():
    """Get installed spaCy major.minor version."""
    try:
        import spacy
        parts = spacy.__version__.split(".")
        return int(parts[0]), int(parts[1])
    except Exception:
        return None, None

def get_spacy_model_url(major, minor):
    """Return the correct wheel URL for the installed spaCy version."""
    model_versions = {
        (3, 7): "en_core_web_sm-3.7.1",
        (3, 6): "en_core_web_sm-3.6.0",
        (3, 5): "en_core_web_sm-3.5.0",
        (3, 4): "en_core_web_sm-3.4.0",
        (3, 3): "en_core_web_sm-3.3.0",
    }
    key = (major, minor)
    model = model_versions.get(key)
    if not model:
        # Default to latest
        model = "en_core_web_sm-3.7.1"

    base = "https://github.com/explosion/spacy-models/releases/download"
    return f"{base}/{model}/{model}-py3-none-any.whl"

def main():
    print("\n" + "="*55)
    print("  AI Internship Portal — Setup Script")
    print("="*55)
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Working dir: {os.getcwd()}")

    # -------------------------------------------------------
    # Step 1: Install pip packages
    # -------------------------------------------------------
    run(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Step 1/4 — Installing Python packages..."
    )

    # -------------------------------------------------------
    # Step 2: Install spaCy model
    # -------------------------------------------------------
    major, minor = get_spacy_version()

    if major is None:
        print("\n  ❌ spaCy not found after install. Trying again...")
        run(f"{sys.executable} -m pip install spacy==3.7.2", "Reinstalling spaCy...")
        major, minor = 3, 7

    print(f"\n  ✅ spaCy {major}.{minor} detected")
    print("  Installing spaCy English model...")

    # Try the standard download first
    ok = run(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Step 2/4 — Downloading spaCy model (standard method)..."
    )

    if not ok:
        # Fallback: direct wheel URL
        url = get_spacy_model_url(major, minor)
        print(f"\n  Standard download failed. Trying direct URL:\n  {url}")
        ok = run(
            f"{sys.executable} -m pip install {url}",
            "Step 2/4 — Installing spaCy model (direct wheel)..."
        )

    if not ok:
        print("\n  ⚠️  spaCy model install failed.")
        print("  The portal will still run using NLTK-only mode (no spaCy).")
        print("  To install manually later, run:")
        print(f"     pip install {get_spacy_model_url(major, minor)}")

    # -------------------------------------------------------
    # Step 3: Download NLTK data
    # -------------------------------------------------------
    print("\n" + "="*55)
    print("  Step 3/4 — Downloading NLTK data...")
    print("="*55)
    try:
        import nltk
        packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
        for pkg in packages:
            try:
                nltk.download(pkg, quiet=True)
                print(f"  ✅ NLTK: {pkg}")
            except Exception as e:
                print(f"  ⚠️  NLTK {pkg}: {e}")
    except ImportError:
        print("  ❌ NLTK not installed.")

    # -------------------------------------------------------
    # Step 4: Verify setup
    # -------------------------------------------------------
    print("\n" + "="*55)
    print("  Step 4/4 — Verifying installation...")
    print("="*55)

    checks = {
        "Flask":          "import flask; print(flask.__version__)",
        "SQLAlchemy":     "import sqlalchemy; print(sqlalchemy.__version__)",
        "Flask-Login":    "import flask_login; print(flask_login.__version__)",
        "Flask-WTF":      "import flask_wtf; print(flask_wtf.__version__)",
        "PyMySQL":        "import pymysql; print(pymysql.__version__)",
        "scikit-learn":   "import sklearn; print(sklearn.__version__)",
        "NLTK":           "import nltk; print(nltk.__version__)",
        "spaCy":          "import spacy; print(spacy.__version__)",
        "spaCy model":    "import spacy; spacy.load('en_core_web_sm'); print('loaded')",
        "PyPDF2":         "import PyPDF2; print(PyPDF2.__version__)",
        "NumPy":          "import numpy; print(numpy.__version__)",
    }

    all_ok = True
    for name, code in checks.items():
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            ver = result.stdout.strip()
            print(f"  ✅ {name:20s} {ver}")
        else:
            print(f"  ❌ {name:20s} NOT FOUND")
            if name not in ("spaCy model",):
                all_ok = False

    # -------------------------------------------------------
    # Done
    # -------------------------------------------------------
    print("\n" + "="*55)
    if all_ok:
        print("  🎉 Setup complete! Run the portal with:")
        print("     python app.py")
        print("     → Open http://localhost:5000")
    else:
        print("  ⚠️  Setup complete with some warnings.")
        print("     The portal may still run. Try: python app.py")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()
