# **Azure AI Search Synonym Map Manager (Python)**

This repository contains a complete Python example demonstrating how to **create, manage, assign, and validate synonym maps** in **Azure AI Search**.
The code supports:

* Creating synonym maps (equivalency or explicit mapping rules)
* Creating a demo search index
* Assigning a synonym map to all eligible fields
* Assigning a synonym map to a specific field
* Inspecting which fields have synonyms assigned

This project accompanies the blog post:
👉 **[https://serkanaytekin.com/?p=262](https://serkanaytekin.com/?p=262)**
**“The Hidden Power of Synonyms in Azure AI Search”**

---

## 🚀 Features

* Full programmatic management of Azure AI Search synonym maps
* Support for both **equivalency** and **explicit mapping** rule styles
* Automatic assignment of synonyms to all valid fields
* Validation rules for field eligibility
* Safe updating and re-creation behavior
* Utility functions to inspect synonym usage
* Ready-to-run demo index

---

## 📦 Requirements

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

**requirements.txt** should contain at least:

```
azure-search-documents
azure-core
```

---

## 🔧 Setup

Before running the project, update these constants inside `SynonymMapManager`:

```python
_search_service_endpoint = "https://<YOUR-SEARCH-SERVICE>.search.windows.net"
_api_key = "<YOUR-ADMIN-API-KEY>"
```

You must use the **Admin API key**, not a query key.

---

## ▶️ Running the Example

Run the script to:

1. Create the demo index
2. Create or update the synonym map
3. Assign the synonym map to all eligible fields
4. Display fields with assigned synonyms

```bash
python main.py
```

You'll see output like:

```
Index 'demo-tech-index' created.
Synonym map 'tech-synonyms-equivalency' created.
Assigned synonym map 'tech-synonyms-equivalency' to field 'title'
Assigned synonym map 'tech-synonyms-equivalency' to field 'content'
Assigned synonym map 'tech-synonyms-equivalency' to field 'tags'
```

---

## 📘 Code Overview

### **SynonymMapManager**

Handles:

* Creating, updating, deleting synonym maps
* Creating a demo index
* Assigning synonyms to individual fields or all eligible fields
* Listing all fields that use a synonym map

### **Synonym Rules**

Example equivalency rule:

```
ui, "user interface", frontend
```

Explicit mapping rule:

```
ui => "user interface"
```

Rules follow the Apache Solr **SynonymGraphFilter** format.

---

## 🧪 Testing Synonym Behavior

After running the script, you can inspect synonym assignments:

```python
manager.list_fields_with_synonym_maps("demo-tech-index")
```

Or test queries in your application:

```
search for: ui
results include: "user interface"
```

No reindexing is required.
Synonyms take effect immediately at **query time**.

---

## 📝 Blog Post

The detailed explanation, architecture background, and step-by-step guide are available in the blog post:

👉 **[https://serkanaytekin.com/?p=262](https://serkanaytekin.com/?p=262)**

---

## 📄 License

This project is provided under the MIT License.
Feel free to use, modify, and adapt it for your own Azure AI Search projects.
