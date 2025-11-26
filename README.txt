#### INPUTS
enriched_demo:  jsonl input format of all revisions of select full articles
enriched_sample_subset:  jsonl input format of the sample revisions obtained after subsampling

#### OUTPUTS
revision_cluster_sorted.csv: the actual LLM-generated revision judgement text (lemmatized and original) of each assigned cluster
bertopic_per_cluster_topic_assignments_sorted.csv: the actual LLM-generated revision judgement text (lemmatized and original) of each BERTopic-extracted topic per assigned cluster

bertopic_general_corpus_topic_assignments_sorted.csv: the actual LLM-generated revision judgement text (lemmatized and original) of each BERTopic-extracted topic from the entire subsampled corpus

csv_files_demo: LLM weaponization detection results of all revisions of select full articles
csv_files_sample_subset: LLM weaponization detection results of the sample revisions obtained after subsampling

/keywords: keyword extraction results 
keywords/cluster_keywords_sorted: keywords per obtained cluster extracted via KeyBERT
keywords/cluster_topics_per_cluster_bertopic_sorted.csv: keywords of whatever topic that can be extracted per obtained cluster extracted via BERTopic
keywords/general_corpus_topics_bertopic_sorted.csv: keywords of topics extracted via BERTopic across the entire 


#### Statistics

Total number of sample revisions after subsampling: 12659
Total number of sample WEAPONIZED revisions after subsamping: 3964
Total number of sample NOT WEAPONIZED revisions after subsamping: 8695

Cluster distributions:
Cluster 0 (35 comments)
Cluster 1 (1004 comments)
Cluster 2 (49 comments)
Cluster 3 (33 comments)
Cluster 4 (83 comments)
Cluster 5 (50 comments)
Cluster 6 (60 comments)
Cluster 7 (79 comments)
Cluster 8 (46 comments)
Cluster 9 (64 comments)
Cluster 10 (31 comments)
Cluster 11 (40 comments)
Cluster 12 (55 comments)
Cluster 13 (34 comments)
Cluster 14 (85 comments)
Cluster 15 (64 comments)
Cluster 16 (123 comments)
Cluster 17 (28 comments)
Cluster 18 (52 comments)
Cluster 19 (307 comments)
Cluster 20 (114 comments)
Cluster 21 (22 comments)
Cluster 22 (34 comments)
Cluster 23 (38 comments)
Cluster 24 (24 comments)
Cluster 25 (62 comments)
Cluster 26 (59 comments)
