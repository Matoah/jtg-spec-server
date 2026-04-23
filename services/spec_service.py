from workflow.index import invoke_workflow, invoke_workflow_async

class SpecService:

    @classmethod
    def query(cls, args):
        query = args.get("query","")
        streaming = args.get("streaming", False)
        if streaming:
            return invoke_workflow_async(query)
        else:
            return invoke_workflow(query)

