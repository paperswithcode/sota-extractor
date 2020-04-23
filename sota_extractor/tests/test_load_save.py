from sota_extractor.taskdb.v01 import taskdb


def test_load_save():
    tdb = taskdb.TaskDB()
    tdb.load_tasks(["data/tasks/nlpprogress.json"])
    tdb.export_to_file("test.json")
