# Question C - Public Health Knowledge Base Documents

This directory contains public health documents collected from the World Health Organization (WHO) to serve as the ground-truth corpus for the Question C Retrieval-Augmented Generation (RAG) system.

## Source Inventory

| Source ID | Topic | Official Title | Organization | Source URL |
|---|---|---|---|---|
| `who_diabetes` | Diabetes | Diabetes | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/diabetes |
| `who_hypertension` | Hypertension | Hypertension | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/hypertension |
| `who_physical_activity` | Physical Activity | Physical activity | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/physical-activity |
| `who_healthy_diet` | Healthy Diet | Healthy diet | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/healthy-diet |
| `who_obesity` | Obesity and Overweight | Obesity and overweight | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight |

## Directory Structure

```text
question_c/documents/
├── who_diabetes.txt
├── who_hypertension.txt
├── who_physical_activity.txt
├── who_healthy_diet.txt
├── who_obesity.txt
├── README.md
└── collection_notes.md
```

## Document Format

Each text file begins with standard metadata headers followed by the cleaned text body:

```text
SOURCE_ID: <source_id>
TITLE: <official title>
ORGANIZATION: World Health Organization
SOURCE_URL: <source_url>
TOPIC: <topic>

<cleaned document text with preserved headings and lists>
```
