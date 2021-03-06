import click
from google.cloud import bigquery

uni1 = 'yf2486' # Your uni
uni2 = 'None' # Partner's uni. If you don't have a partner, put None

# Test function
def testquery(client):
    q = """select * from `w4111-columbia.graph.tweets` limit 50"""
    job = client.query(q)

    # waits for query to execute and return
    results = job.result()
    return list(results)

# SQL query for Question 1. You must edit this funtion.
# This function should return a list of IDs and the corresponding text.
def q1(client):
    q1 = """select id from `w4111-columbia.graph.tweets` where text LIKE '%going live%www.twitch%' OR text LIKE '%www.twitch%going live%'"""
    job = client.query(q1)
    
    results = job.result()
    return list(results)

# SQL query for Question 2. You must edit this funtion.
# This function should return a list of days and their corresponding average likes.
def q2(client):
    # Select the first 3 letters in create_time, which is the day
    q2 = """select substr(create_time, 1, 3) as day from `w4111-columbia.graph.tweets` group by day order by avg(like_num) DESC limit 1"""
    job = client.query(q2)
    
    results = job.result()
    return list(results)

# SQL query for Question 3. You must edit this funtion.
# This function should return a list of source nodes and destination nodes in the graph.
def q3(client):
    q3 = """create or replace table dataset.edges as (select distinct * from (select twitter_username as src, Regexp_extract(text,r"[@]([\w_-]+)") as dst from `w4111-columbia.graph.tweets` where Regexp_extract(text,r"([@][\w_-]+)") != '' ))"""
    job = client.query(q3)
    
    return []

# SQL query for Question 4. You must edit this funtion.
# This function should return a list containing the twitter username of the users having the max indegree and max outdegree.
def q4(client):
    q4 = """select src, dst from (select src, count(*) as s_count from dataset.edges group by src), (select dst, count(*) as d_count from dataset.edges group by dst) where s_count = (select max(s_count) as max_outdegree from (select src, count(*) as s_count from dataset.edges group by src)) And d_count = (select max(d_count) as max_indegree from (select dst, count(*) as d_count from dataset.edges group by dst))""" 
    job = client.query(q4)
    
    results = job.result()
    return list(results)

# SQL query for Question 5. You must edit this funtion.
# This function should return a list containing value of the conditional probability.
def q5(client):
    q5 = """create or replace table dataset.indegree as (select dst,count(*) count from dataset.edges group by dst)
    create or replace table dataset.avg_likes as (select twitter_username, sum(like_num)/count(*) likes from `w4111-columbia.graph.tweets` group by twitter_username)
    create or replace table dataset.popular as (select distinct w.twitter_username from dataset.avg_likes a, dataset.indegree i, `w4111-columbia.graph.tweets` w where a.likes > (select avg(like_num) from `w4111-columbia.graph.tweets`) and i.count > (select avg(count) from dataset.indegree) and w.twitter_username = a.twitter_username and w.twitter_username = i.dst)
    create or replace table dataset.unpopular1 as (select distinct w.twitter_username from dataset.avg_likes a, dataset.indegree i, `w4111-columbia.graph.tweets` w where a.likes < (select avg(like_num) from `w4111-columbia.graph.tweets`) and w.twitter_username = a.twitter_username and i.count < (select avg(count) from dataset.indegree) and w.twitter_username = i.dst)
    create or replace table dataset.unpopular2 as (select distinct w.twitter_username from dataset.avg_likes a, `w4111-columbia.graph.tweets` w where a.likes < (select avg(like_num) from `w4111-columbia.graph.tweets`) and w.twitter_username = a.twitter_username and w.twitter_username not in (select dst from dataset.indegree))
    create or replace table dataset.unpop_mention_pop as (select src,dst from dataset.edges where dst in (select twitter_username from dataset.popular) and src in (select twitter_username from dataset.unpopular1) or src in (select twitter_username from dataset.unpopular2))
    select count(m.src)/count(w.twitter_username) popular_unpopular from dataset.unpop_mention_pop m, `w4111-columbia.graph.tweets` w where w.twitter_username in (select twitter_username from dataset.unpopular1) or w.twitter_username in (select twitter_username from dataset.unpopular2)"""
    job = client.query(q5)
    
    results = job.result()
    return list(results)

# SQL query for Question 6. You must edit this funtion.
# This function should return a list containing the value for the number of triangles in the graph.
def q6(client):
    q6 = """select count(*) as no_of_triangles from (dataset.edges e1 join dataset.edges e2 on e1.dst = e2.src) join dataset.edges e3 on e2.dst = e3.src"""
    job = client.query(q6)

    results = job.result()
    return list(results)

# SQL query for Question 7. You must edit this funtion.
# This function should return a list containing the twitter username and their corresponding PageRank.
def q7(client):

    return []


# Do not edit this function. This is for helping you develop your own iterative PageRank algorithm.
def bfs(client, start, n_iter):

    # You should replace dataset.bfs_graph with your dataset name and table name.
    q1 = """
        CREATE TABLE IF NOT EXISTS dataset.bfs_graph (src string, dst string);
        """
    q2 = """
        INSERT INTO dataset.bfs_graph(src, dst) VALUES
        ('A', 'B'),
        ('A', 'E'),
        ('B', 'C'),
        ('C', 'D'),
        ('E', 'F'),
        ('F', 'D'),
        ('A', 'F'),
        ('B', 'E'),
        ('B', 'F'),
        ('A', 'G'),
        ('B', 'G'),
        ('F', 'G'),
        ('H', 'A'),
        ('G', 'H'),
        ('H', 'C'),
        ('H', 'D'),
        ('E', 'H'),
        ('F', 'H');
        """

    job = client.query(q1)
    results = job.result()
    job = client.query(q2)
    results = job.result()

    # You should replace dataset.distances with your dataset name and table name. 
    q3 = """
        CREATE OR REPLACE TABLE dataset.distances AS
        SELECT '{start}' as node, 0 as distance
        """.format(start=start)
    job = client.query(q3)
    # Result will be empty, but calling makes the code wait for the query to complete
    job.result()

    for i in range(n_iter):
        print("Step %d..." % (i+1))
        q1 = """
        INSERT INTO dataset.distances(node, distance)
        SELECT distinct dst, {next_distance}
        FROM dataset.bfs_graph
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


# Do not edit this function. You can use this function to see how to store tables using BigQuery.
def save_table():
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

@click.command()
@click.argument("PATHTOCRED", type=click.Path(exists=True))
def main(pathtocred):
    client = bigquery.Client.from_service_account_json(pathtocred)

    funcs_to_test = [q1, q2, q3, q4, q5, q6, q7]
    #funcs_to_test = [testquery]
    for func in funcs_to_test:
        rows = func(client)
        print ("\n====%s====" % func.__name__)
        print(rows)

    #bfs(client, 'A', 5)

if __name__ == "__main__":
  main()
