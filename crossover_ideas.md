1.  Randomly choose schedule
    - not really cross over
    - really easy
2.  Average task counters and randomly create schedule
    - Adding too much random
    - Second easiest I think
3.  Like merge sort; start at 0 at each list, go through adding to schedule, if
    task is done skip task, continue until schedule is filled
    - Might be the best idea; keeps the ideas of crossover without lossing task
        lengths
    - Complicated as fuck
4.  Only keep matching schedule
    - Might be good. We are only keep the ones that we know both good schedule
        have
    - Bad cause we might lose a good portion of our schedule
    _ _idea_: we might be able to change mutate rates to add tasks more often
        to make up for this loss of tasks
