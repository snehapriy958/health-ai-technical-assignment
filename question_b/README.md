# Question B — Risk Prediction Application

## Objective

Build a small health-risk prediction application around a trained
machine-learning model.

## Level 1

Requirements:

1. Train a classification model.
2. Serve the model through FastAPI or Flask.
3. Implement a `/predict` endpoint.
4. Create a small frontend.
5. Display the predicted risk clearly to the user.

## Level 2

Requirements:

1. Store prediction requests and results in a database.
2. Implement `/stats`.
3. Use hand-written SQL rather than an ORM.
4. Return:
   - Total prediction requests
   - Average predicted risk
   - Share of high-risk predictions
5. Validate inputs.
6. Write at least three pytest tests, including invalid input.

## Level 3

Requirements:

1. Intentionally break the application in two different ways.
2. Demonstrate the failures.
3. Diagnose and fix them.
4. Explain the engineering decisions.
5. Discuss safety considerations for approximately 100 concurrent users.

## Personal Seed

`S = 48`

The same seed must be used wherever randomness is involved.

## Run Instructions

To be added after implementation.

## Results

To be added after experiments.