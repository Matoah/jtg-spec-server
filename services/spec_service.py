from workflow.index import invoke_workflow

class SpecService:

    @classmethod
    def query(cls, args):
        query = args.get("query","")
        return invoke_workflow(query)

