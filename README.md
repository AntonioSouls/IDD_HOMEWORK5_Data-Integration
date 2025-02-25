# <div align="center"> HOMEWORK 5: DATA INTEGRATION </div>
This repository contains the fifth homework assigned to us during the Data Engineering course. It was created with the aim of making public the solution that my colleague @danielluca00 and I devised and proposed to solve the tasks assigned to us by the delivery.

## - Homework Goals
In the age of Data Science, data integration is a crucial element to ensure accurate analysis and informed decisions. Business information often comes from heterogeneous sources, with different formats and structures, making it difficult to use effectively. 
A well-designed Data Integration system allows these data to be unified and harmonised, improving the quality and reliability of the information available to companies.
Therefore, this project is very important in order to provide a solution that can automate the Data Integration process, where necessary.

## - Homework Requirements
 The data integration process consists of three basic steps:
 1) **Schema Alignment:** this consists of identifying and mapping common fields between different data sources, creating a coherent mediated schema;
 2) **Populating the mediated schema:** This consists of inserting the data from the various sources into the mediated schema we have created, trying to match the attributes of the source data with the corresponding attributes of the mediated schema;
 3) **Record Linkage:** involves the comparison and association of records that represent the same entity but come from different databases;

## - Description of Our Solution
Our solution involves extracting the information from the source tables in a format understandable to an LLM. From each table, in fact, information is extracted in a ‘cleaner’ format and this information is passed to the LLM, which returns a description of each attribute of that table passed to it. 
All the descriptions of each table are then placed entirely in a single json format file which is then passed back to the model with a new prompt. 
This second operation (accompanied by careful manual review) allows us to obtain the attributes to be inserted into the mediated schema, and for each attribute, it also tells us the attributes of the source schemas that correspond to that selected attribute of the mediated schema. 
In this way, then, we obtain the mediated schema which, by means of the Python script mediated_schema_population.py, is populated with data.
At this point, the Record Linkage phase begins.
This phase is, in turn, divided into two sub-phases:
- **Blocking =** Which allows to group in blocks the lines of the averaged pattern potentially considered similar;
- **Pairwise matching =** Which checks which of the rows of the same block refer to the same entity;
Blocking involves the use of two strategies:
1) **LOCALITY SENSITIVE HASHING =** That creates a hash of the various rows of the mediated scheme based on tokenization by words and inserts all the rows that have the same hash in the same block;
2) **TRIGRAM HASHING =** It does the same thing but doing a hash based on trigram tokenization
Both strategies provide results on which two Pairwise Matching strategies are applied:
1) **RECORD LINKAGE TOOLKIT =** library that uses the JaroWinkler metric to check the similarity between two elements in the same block
2) **DITTO =** Pre-trained neural network on a training set created manually with the purpose of making predictions on which elements of the same block refer to the same entity
Following all these tests, we measured the performance of the various solutions, discovering that applying Ditto on a block made with trigrams is the best performing strategy
