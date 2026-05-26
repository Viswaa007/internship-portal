# =============================================================
# File: backend/ai/performance_predictor.py
# Purpose: AI-based student performance prediction
#          Uses Logistic Regression + Random Forest
#          Input: attendance%, task completion%, reports, rating
#          Output: Excellent / Good / Average / Needs Improvement
# =============================================================

import numpy as np

# ---------------------------------------------------------------
# Scikit-learn imports
# ---------------------------------------------------------------
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Using rule-based prediction.")

import os

# Path to save/load trained model
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, 'performance_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')

# ---------------------------------------------------------------
# Performance labels
# ---------------------------------------------------------------
PERFORMANCE_LABELS = {
    0: 'Needs Improvement',
    1: 'Average',
    2: 'Good',
    3: 'Excellent'
}

PERFORMANCE_COLORS = {
    'Excellent': '#28a745',
    'Good': '#17a2b8',
    'Average': '#ffc107',
    'Needs Improvement': '#dc3545'
}


class PerformancePredictor:
    """
    Predicts student performance using ensemble ML models.

    Features used for prediction:
    1. attendance_pct     - % of days present
    2. task_completion    - % of tasks completed
    3. report_submissions - number of approved reports
    4. mentor_rating      - average mentor rating (1-5)

    Algorithm:
    - Primary: Random Forest Classifier (robust, interpretable)
    - Secondary: Logistic Regression (fast baseline)
    - Final: Weighted ensemble of both
    """

    def __init__(self):
        self.rf_model = None
        self.lr_model = None
        self.scaler = None
        self.is_trained = False

        # Try to load existing model
        if SKLEARN_AVAILABLE:
            self._load_or_train_model()

    def _generate_training_data(self, n_samples=500):
        """
        Generate synthetic training data with realistic patterns.
        In production, replace with real historical data from the database.
        """
        np.random.seed(42)

        X = []  # Features
        y = []  # Labels

        for _ in range(n_samples):
            # Generate correlated features
            base_performance = np.random.random()

            # Students with high attendance tend to perform better
            attendance = np.clip(base_performance * 100 + np.random.normal(0, 15), 0, 100)
            task_comp = np.clip(base_performance * 100 + np.random.normal(0, 20), 0, 100)
            reports = max(0, int(base_performance * 8 + np.random.normal(0, 2)))
            rating = np.clip(base_performance * 5 + np.random.normal(0, 0.8), 1, 5)

            X.append([attendance, task_comp, reports, rating])

            # Label based on weighted performance score
            score = (attendance * 0.3 + task_comp * 0.35 + (reports / 8 * 100) * 0.15 + (rating / 5 * 100) * 0.2)

            if score >= 80:
                y.append(3)   # Excellent
            elif score >= 65:
                y.append(2)   # Good
            elif score >= 50:
                y.append(1)   # Average
            else:
                y.append(0)   # Needs Improvement

        return np.array(X), np.array(y)

    def _train_model(self):
        """Train both ML models on synthetic data."""
        if not SKLEARN_AVAILABLE:
            return

        print("Training performance prediction model...")

        # Generate training data
        X, y = self._generate_training_data(n_samples=1000)

        # Split into train/test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Scale features (important for Logistic Regression)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.rf_model.fit(X_train_scaled, y_train)
        rf_accuracy = accuracy_score(y_test, self.rf_model.predict(X_test_scaled))

        # Train Logistic Regression
        self.lr_model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced',
            multi_class='multinomial'
        )
        self.lr_model.fit(X_train_scaled, y_train)
        lr_accuracy = accuracy_score(y_test, self.lr_model.predict(X_test_scaled))

        print(f"Random Forest Accuracy: {rf_accuracy:.2%}")
        print(f"Logistic Regression Accuracy: {lr_accuracy:.2%}")

        # Save models to disk for future use
        try:
            joblib.dump(self.rf_model, MODEL_PATH.replace('.pkl', '_rf.pkl'))
            joblib.dump(self.lr_model, MODEL_PATH.replace('.pkl', '_lr.pkl'))
            joblib.dump(self.scaler, SCALER_PATH)
            print("Models saved successfully!")
        except Exception as e:
            print(f"Warning: Could not save models: {e}")

        self.is_trained = True

    def _load_or_train_model(self):
        """Load existing model or train a new one."""
        rf_path = MODEL_PATH.replace('.pkl', '_rf.pkl')
        lr_path = MODEL_PATH.replace('.pkl', '_lr.pkl')

        try:
            if os.path.exists(rf_path) and os.path.exists(lr_path) and os.path.exists(SCALER_PATH):
                self.rf_model = joblib.load(rf_path)
                self.lr_model = joblib.load(lr_path)
                self.scaler = joblib.load(SCALER_PATH)
                self.is_trained = True
                print("Loaded existing performance prediction models.")
            else:
                self._train_model()
        except Exception as e:
            print(f"Error loading models: {e}. Retraining...")
            self._train_model()

    def _rule_based_prediction(self, attendance_pct, task_completion, report_submissions, mentor_rating):
        """
        Fallback rule-based prediction when scikit-learn is not available.
        Based on weighted scoring.
        """
        # Normalize inputs
        attendance_score = min(attendance_pct, 100)
        task_score = min(task_completion, 100)
        report_score = min(report_submissions * 10, 100)  # 10 points per report
        rating_score = (mentor_rating / 5) * 100

        # Weighted average
        total_score = (
            attendance_score * 0.30 +
            task_score * 0.35 +
            report_score * 0.15 +
            rating_score * 0.20
        )

        if total_score >= 80:
            return 'Excellent', total_score
        elif total_score >= 65:
            return 'Good', total_score
        elif total_score >= 50:
            return 'Average', total_score
        else:
            return 'Needs Improvement', total_score

    def predict(self, attendance_pct, task_completion, report_submissions, mentor_rating=3.0):
        """
        Predict student performance.

        Args:
            attendance_pct (float): Attendance percentage (0-100)
            task_completion (float): Task completion rate (0-100)
            report_submissions (int): Number of approved report submissions
            mentor_rating (float): Average mentor rating (1-5)

        Returns:
            dict with prediction, confidence, score breakdown, and recommendations
        """
        # Clamp inputs to valid ranges
        attendance_pct = max(0, min(100, float(attendance_pct)))
        task_completion = max(0, min(100, float(task_completion)))
        report_submissions = max(0, int(report_submissions))
        mentor_rating = max(1, min(5, float(mentor_rating)))

        # Use rule-based if sklearn not available
        if not SKLEARN_AVAILABLE or not self.is_trained:
            label, score = self._rule_based_prediction(
                attendance_pct, task_completion, report_submissions, mentor_rating
            )
            return self._build_response(label, score, attendance_pct, task_completion,
                                        report_submissions, mentor_rating)

        try:
            # Prepare feature vector
            features = np.array([[attendance_pct, task_completion, report_submissions, mentor_rating]])
            features_scaled = self.scaler.transform(features)

            # Get predictions from both models
            rf_pred = self.rf_model.predict(features_scaled)[0]
            rf_proba = self.rf_model.predict_proba(features_scaled)[0]

            lr_pred = self.lr_model.predict(features_scaled)[0]
            lr_proba = self.lr_model.predict_proba(features_scaled)[0]

            # Ensemble: weighted average of probabilities (RF gets more weight)
            ensemble_proba = 0.65 * rf_proba + 0.35 * lr_proba
            final_pred = int(np.argmax(ensemble_proba))
            confidence = float(np.max(ensemble_proba)) * 100

            label = PERFORMANCE_LABELS[final_pred]

            # Calculate weighted score for display
            score = (attendance_pct * 0.30 + task_completion * 0.35 +
                    min(report_submissions * 10, 100) * 0.15 +
                    (mentor_rating / 5 * 100) * 0.20)

            return self._build_response(label, score, attendance_pct, task_completion,
                                        report_submissions, mentor_rating, confidence)

        except Exception as e:
            print(f"ML prediction failed: {e}. Using rule-based fallback.")
            label, score = self._rule_based_prediction(
                attendance_pct, task_completion, report_submissions, mentor_rating
            )
            return self._build_response(label, score, attendance_pct, task_completion,
                                        report_submissions, mentor_rating)

    def _build_response(self, label, score, attendance_pct, task_completion,
                        report_submissions, mentor_rating, confidence=None):
        """Build a comprehensive response dictionary."""

        # Generate recommendations
        recommendations = []
        if attendance_pct < 75:
            recommendations.append("Improve attendance - aim for at least 90%")
        if task_completion < 70:
            recommendations.append("Complete assigned tasks on time")
        if report_submissions < 3:
            recommendations.append("Submit more progress reports regularly")
        if mentor_rating < 3.5:
            recommendations.append("Engage more actively with mentor feedback")

        if not recommendations:
            recommendations.append("Excellent work! Keep maintaining this performance.")

        return {
            'performance_grade': label,
            'overall_score': round(score, 2),
            'confidence': round(confidence, 2) if confidence else None,
            'color': PERFORMANCE_COLORS.get(label, '#6c757d'),
            'breakdown': {
                'attendance': attendance_pct,
                'task_completion': task_completion,
                'report_submissions': report_submissions,
                'mentor_rating': mentor_rating,
                'attendance_score': round(attendance_pct * 0.30, 2),
                'task_score': round(task_completion * 0.35, 2),
                'report_score': round(min(report_submissions * 10, 100) * 0.15, 2),
                'rating_score': round((mentor_rating / 5 * 100) * 0.20, 2),
            },
            'recommendations': recommendations,
            'model_used': 'Ensemble (Random Forest + Logistic Regression)' if SKLEARN_AVAILABLE else 'Rule-Based'
        }

    def get_feature_importance(self):
        """Get feature importance from Random Forest model."""
        if not self.rf_model or not SKLEARN_AVAILABLE:
            return {}

        feature_names = ['Attendance %', 'Task Completion %', 'Report Submissions', 'Mentor Rating']
        importances = self.rf_model.feature_importances_

        return dict(zip(feature_names, [round(float(i) * 100, 2) for i in importances]))


# ---------------------------------------------------------------
# Test the module directly
# ---------------------------------------------------------------
if __name__ == '__main__':
    print("Performance Predictor Test")
    print("=" * 50)

    predictor = PerformancePredictor()

    test_cases = [
        (95, 90, 5, 4.8, "Expected: Excellent"),
        (80, 75, 3, 3.5, "Expected: Good"),
        (65, 60, 2, 3.0, "Expected: Average"),
        (50, 40, 1, 2.0, "Expected: Needs Improvement"),
    ]

    for attendance, task, reports, rating, expected in test_cases:
        result = predictor.predict(attendance, task, reports, rating)
        print(f"\nInput: Attendance={attendance}%, Tasks={task}%, Reports={reports}, Rating={rating}")
        print(f"Predicted: {result['performance_grade']} (Score: {result['overall_score']})")
        print(f"Comment: {expected}")
        print(f"Recommendations: {result['recommendations']}")

    print("\nFeature Importance:")
    print(predictor.get_feature_importance())
