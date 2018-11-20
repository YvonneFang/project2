### Project 2: Graph Analysis

* Released: 11/20
* Due: 12/10 10AM
* Value: 5% of your grade
* Max team of 2

Many graph analysis compute network centrality, density, shortest paths, and other path-based statistics about a graph.  It may seem that writing a one-off Python script is a good way to perform this analysis, but it turns out that SQL is pretty great at doing this type of analysis!  


For this assignment, you will replicate a summer research project to analyze Tweets from [Twitch streamers](http://www.twitch.com).  Twitch is an online platform for live-streaming people playing video games (and other activities such as cooking).   Our research group downloaded the tweets written by a set of Twitch streamers and are interested in understanding the types of tweets and the relationships between Twitch streamers.  


### Assignment Details

#### Refresher

You will write queries or short Python programs to answer the following questions about the dataset.  

In the simple case, graphs have the following schema:

        nodes(id int primary key, <attributes>)
        edges(
          src int NOT NULL references nodes(id),
          dst int NOT NULL references nodes(id),
          <attributes
        )

Recall that in graph analysis, you are interested in finding neighbors of nodes or paths between nodes.    Following an edge in the graph corresponds to a JOIN.  For example, the following finds all neighbors of node id 2:

        SELECT dst FROM edges WHERE src = 2;

Similarly, if we have a table `goodnodes` that contains IDs of nodes that we are interested in, the following query finds neighbors of these good nodes:

        SELECT dst FROM edges, goodnodes WHERE edges.src = goodnodes.id;

#### The Twitter dataset

In reality, the twitter dataset isn't as neat as the above example.  Instead it contains the following attributes:

        idx                 INTEGER   # aribtrary idx value
        create_time         STRING
        id                  FLOAT     # Tweet id
        in_reply            STRING    # id of Tweet that this row is replying to, or Null
        like_num            FLOAT     # number of likes
        quoted_org_id       FLOAT     # id of orig tweet if this row quotes another tweet
        retweet_num         FLOAT     # number of times this row was retweeted
        retweet_org_id      FLOAT     # id of orig tweet if this row is a retweet
        text                STRING    
        twitter_username    STRING    
        twitch_username     STRING   

The edges in the graph are based on the `in_reply` attribute, which is the `id` of the Tweet that the current tweet is in response to.  Alternatively, there may be implicit edges if the `text` of the Tweet contains an "@USERNAME" substring.  

#### Setup
To analyze the data you will be using BigQuery. It is a service that enables interactive analysis of massively large datasets working in conjunction with Google Storage. You will need to setup your local development environment and obtain the required credentials file for using the BigQuery API. Follow the instructions provided in the [Setup Instructions PDF](https://github.com/w4111/project2/blob/master/Project%20Setup%20Instructions.pdf) for setting up your environment and for obtaining your credentials. Please make sure that you don't share your credentials anywhere. DO NOT upload it to Github or anywhere else. You must also make sure that you create a dataset on BigQuery as mentioned in the instructions because otherwise you will not be able to create new tables. 


We have [provided a starter script for you to edit](./graph.py). You must edit this file and submit it. 

Once you successfully setup your local development environment, then you can edit [graph.py](./graph.py) to update the `PATHTOCRED` variable to where you stored the credentials file and then run the script.  

        python graph.py <path to credentials file>

References

* https://cloud.google.com/bigquery/create-simple-app-api#bigquery-simple-app-local-dev-python


### Queries

Implement the functions in the Python file to return the rows corresponding to the answers to the following questions:

##### Q1

Many Twitch streamers will tweet that they are starting a live broadcast beforehand as a way to advertise themselves.  
Find the `id` of Tweets that contain both the phrase "going live" and a URL to twitch.com.  

For example:

* "I'm going live now at http://www.twitch.com/blah/stream/" is a match
* "I'm going live!" is not a match

Your answer should be a single query containing the columns:
- id (id of the tweets)
- text (text of the tweets) 

##### Q2
Engagement for Twitch streamers with their followers can be measured by the number of likes they get on their tweets. Find out which day of the week on average gets the maximum number of likes.

Your answer should be a single query containing the columns:
- day (day of the week)
- avg_likes (average number of likes for the day) 

##### Q3

Twitch streamers sometimes @ mention other streamers in their tweets by adding a "@" prefix to the other streamer's Twitter username.  For instance, the following tweet mentions `anotheruser`.

      Thanks to @anotheruser for a great broadcast!

Take a look at the [regular expressions documentation for BigQuery](https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators#regexp_extract).    

Find all the tweets that @ mention another user. The tweets mentioning other users can be looked at as a directed edge from the tweeter to the mentioned user and hence we can look at it as a directed graph where each row is an edge between a tweeter and the user that the tweet mentions. Create a table “GRAPH” with column names src and dst which stores the edge list of the graph. You must store only the distinct edges in the table.

Your answer should be a single query containing the columns:
- src (the twitter_username of the user)
- dst (the twitter_username of the user mentioned in the tweet)

In case more than one user has been mentioned in a tweet, you must consider only the user which has been mentioned first. 

You should save this table because you will be using it for the next few questions. Look at the example provided below to see how you can save tables on BigQuery using the Python API. 

    from google.cloud import bigquery
    client = bigquery.Client()
    dataset_id = 'dataset'

    job_config = bigquery.QueryJobConfig()
    # Set use_legacy_sql to True to use legacy SQL syntax.
    job_config.use_legacy_sql = True
    # Set the destination table
    table_ref = client.dataset(dataset_id).table('test')
    job_config.destination = table_ref
    job_config.allow_large_results = True
    sql = """select * from [w4111-columbia.graph.tweets] limit 3"""

    # Start the query, passing in the extra configuration.
    query_job = client.query(
        sql,
        # Location must match that of the dataset(s) referenced in the query
        # and of the destination table.
        location='US',
        job_config=job_config)  # API request - starts the query

    query_job.result()  # Waits for the query to finish
    print('Query results loaded to table {}'.format(table_ref.path))

The dataset_id refers to the name of the dataset which you created and the table_ref variable specifies the name of the table to which the results will be saved into. 
For further reference, you can check the following link: [Saving Results to Table](https://cloud.google.com/bigquery/docs/writing-results).

##### Q4
The indegree of a node in a directed graph is defined as the number of edges which are incoming on the node. Similarly, the outdegree of a node in a directed graph is defined as the number of edges which are outgoing from the node. For more information, you can read - [Indegree and Outdegree](https://en.wikipedia.org/wiki/Directed_graph#Indegree_and_outdegree)

Using this information, find out from the GRAPH table which user has the highest indegree and which user has the highest outdegree.

Your answer should be a single query containing the columns:
- max_indegree
- max_outdegree

##### Q5
Let us define 4 categories of Twitter users. We will use the average number of likes a user gets on his/her tweets as the first metric and the number of times they are mentioned by other users in tweets (i.e. indegree) as the second metric. Then we can classify each user as follows:
- High indegree, high average number of likes 
- High indegree, low average number of likes
- Low indegree, high average number of likes
- Low indegree, low average number of likes

We will refer to the 'low indegree, low average likes' category of users as "unpopular" users and 'high indegree, high average likes' category of users as "popular" users. 

We define the indegree and average number of likes to be high or low based on the rules below:
1) If indegree < avg(indegree) of all the nodes in the graph then indegree is said to be low for the user, else it is considered high.
2) If the average number of likes for user < average number of likes for all the nodes in the graph, then the average number of likes is said to be low for the user; else it is considered high.

Now, you need to find the conditional probability, that given an unpopular user, what is the probability that they mention a popular user in their tweets i.e. find P(@ mentions popular user | is unpopular).

Your answer should be a query containing the column:
- popular_unpopular (conditional probability P(@ mentions popular user | is unpopular))

##### Q6
Given a graph G = (V, E), a “triangle” is a set of three vertices that are mutually adjacent in G i.e. given 3 nodes of a graph A, B, C there exist edges A->B, B->C and C->A which form a triangle in the graph. From the graph table which you created above, find out the number of triangles in the graph.

For the first part, your answer should be a single query containing the column:
- no_of_triangles

##### Q7
The PageRank algorithm is used to rank the importance of nodes in a graph. It works by counting the number of edges incident to a node to determine how important the node is. The underlying assumption is that more important nodes are likely to receive more links from other nodes. Find the top 100 nodes with the highest PageRank in the graph.
Hint: It is not possible to use "WITH RECURSIVE" on BigQuery. You must develop a recursive implementation for PageRank. You can look at the recursive implementation of BFS provided below to get started.

You must run the algorithm for 20 iterations and your output table should contain the following columns:
- twitter_username (the twitter_username of the user)
- PageRank

You must implement only the simplified version of the PageRank algorithm. 
This algorithm works as follows - Assume a small universe of four web pages: A, B, C and D. PageRank is initialized to the same value for all pages since we assume a probability distribution between 0 and 1 as the PageRank for each node. Hence the initial value for each page in this example is 0.25. If the only links in the system were from pages B->A, C->A and D->A, each link would transfer 0.25 PageRank to A upon the next iteration, for a total of 0.75 i.e. PR(A) = PR(B) + PR(C) + PR(D). 

Now, suppose instead that we have the links B->C, B->A, C->A, D->A, D->B, D->C. Thus, upon the first iteration, page B would transfer half of its existing value, or 0.125, to page A and the other half, or 0.125, to page C. Page C would transfer all of its existing value, 0.25, to the only page it links to, A. Since D had three outbound links, it would transfer one third of its existing value, or approximately 0.083, to A. At the completion of this iteration, page A will have a PageRank of approximately 0.458.
PR(A)=PR(B)/2 + PR(C)/1 + PR(D)/3.

Thus, we can write the PageRank of A as:
PR(A)= PR(B)/L(B) + PR(C)/L(C) + PR(D)/L(D) where L(x) gives us the number of outbound links for any node x. 

In general, the PageRank value for a page u is dependent on the PageRank values for each page v contained in the set containing all pages linking to page u, divided by the number of links from page v. 
It is given by the formula: ![](https://www.geeksforgeeks.org/wp-content/ql-cache/quicklatex.com-aafd3a0d9f8bb8325cf2b41a4a839bbf_l3.svg)

To read more about PageRank, you can refer to the following link: [PageRank](http://home.ie.cuhk.edu.hk/~wkshum/papers/pagerank.pdf)


### Starter Code
You can use the starter code provided in the graph.py file. You should write SQL queries for all the questions. To check if your environment has been setup correctly, you can run the graph.py file as follows:        
        
        python graph.py [path_to_credentials_file]

If everything has been setup correctly, you must be able to see the output for the testquery function inside the graph.py file.

To start working on your solutions, you must write queries for each question inside the corresponding functions.

For q7, you will need to develop an iterative solution. Look at the following iterative implementation of Breadth First Search:

     def bfs(client, start, n_iter):
            
            q1 = """
                CREATE TABLE IF NOT EXISTS bfs_graph (src string, dst string);
                """
            q2 = """
                INSERT INTO bfs_graph VALUES
                ('A', 'B'),
                ('A', 'E'),
                ('B', 'C'),
                ('C', 'D'),
                ('E', 'F'),
                ('F', 'D');
                ('A', 'F'),
                ('B', 'E'),
                ('B', 'F'),
                ('A', 'G'),
                ('B', 'G'),
                ('F', 'G');
                ('H', 'A'),
                ('G', 'H'),
                ('H', 'C'),
                ('H', 'D'),
                ('E', 'H'),
                ('F', 'H');
                """
            
            job = client.query(q1)
            job.result()
            job = client.query(q2)
            job.result()
            
            q3 = """
            CREATE OR REPLACE TABLE dataset.distances AS
            SELECT '{start}' as node, 0 as distance
            """.format(start=start)
            job = client.query(q3)
            # Result will be empty, but calling makes the code wait for the query to complete
            job.result()

            for i in range(n_iter):
                print "Step %d..." % (i+1)
                q1 = """
                INSERT INTO dataset.distances(node, distance)
                SELECT distinct dst, {next_distance}
                FROM bfs_graph
                WHERE src IN (
                    SELECT node
                    FROM dataset.distances
                    WHERE distance = {curr_distance}
                    )
                AND dst NOT IN (
                    SELECT node
                    FROM dataset.distances
                    )
                """.format(
                    curr_distance=i,
                    next_distance=i+1
                )
                job = client.query(q1)
                results = job.result()
                # print(results)

You can use the above implementation of the BFS algorithm as a starting point for writing your own iterative implementation of the PageRank algorithm for Q7.

### Submission Instructions
Submit the modified ``graph.py`` file on Courseworks. There should be only one submission per group. You must mention the UNIs of both group members while submitting. You will be graded based on the correctness of your queries. We will execute each query function so each function should be able to be called. We will match the table generated by your query with the solution table for each question.   
