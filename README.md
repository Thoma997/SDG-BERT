# SDG-BERT Project
### Description
The SDG-BERT project is a trial to develop a SDG labelling tool for text data. 
Our approach consists of using RoBERTa, the contextual language model developed by Facebook 
which is the successor of the original Google BERT language model.
Within the scope of the master thesis, for which we are developing this approach, 
the model will be fine tuned on job postings.
Thus, given a job posting, the model will assign labels ranging from 0 to 17 to each paragraph.
We envision, that the summary of labels per job posting reflects the degree of sustainability of a job 
(or at least its advertisement).

### Contribution
To contribute open your terminal and enter the following steps. Lines starting with ```$``` signal code. 
Lines starting with ```#``` signal comments. Do not copy the ```$``` symbols.

Check requirements::
```shell
$ conda --version
# Should output sth like 'conda 4.8.3'.
# Otherwise install conda using e.g. brew.

$ git --version
# Should output something like 'git version 2.13.0'
# Otherwise install git via 'conda install git' command
```

Clone repository: <br>
The following code will create a folder named "sdg-bert-project" on your desktop.
```shell
$ mkdir ~/Desktop/ && cd ~/Desktop/SDG-BERT/
$ git clone https://github.com/Thoma997/SDG-BERT.git
```

Create environment: <br>
```shell
$ ~/Desktop/sdg-bert-project/
$ conda env create -f environment.yaml
$ conda env list
# you should see an environment called 'sdg-bert' now in the list.

$ conda activate sdg-bert
```

Add environment variables:
```shell
Write an email to us in order to get the database access data 
to help us make the translator converge :) 
```

Activate environment and start translator:
```shell
$ conda activate sdg-bert
$ cd ~/Desktop/sdg-bert-project/ && python translator.py >> ~/Desktop/sdg-bert-project/log.txt 2&>1
```