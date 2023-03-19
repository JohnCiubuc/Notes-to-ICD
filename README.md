# Notes-to-ICD
Convert medical documentatio notes into ICD code lists

# Requirements
* pymedtermino
	* Modify `__init__` function to disable multithread checking to work with streamlit
	* Requires snomed ct and icd 10 databases. Please refer to pymedtermino documentation for more information
* streamlit
	* streamlit-extras for tagging text with snomed specificity score