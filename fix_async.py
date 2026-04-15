import json

files = ["benchmark/STT benchmark google speech.ipynb", "STT/STT google speech benchmark.ipynb"]

for filepath in files:
    with open(filepath, 'r') as f:
        nb = json.load(f)

    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])

            # Use await instead of asyncio.run
            if "asyncio.run(provider.transcribe_async(file_name))" in source:
                new_source = source.replace("def process_fileV2(", "async def process_fileV2(")
                new_source = new_source.replace("def process_file(", "async def process_file(")
                new_source = new_source.replace("asyncio.run(provider.transcribe_async(file_name))", "await provider.transcribe_async(file_name)")

                # Split back into lines
                cell['source'] = [line + '\n' for line in new_source.split('\n') if line]

            # In the execution cells, add await
            if "process_file(local_file,model_name)" in source:
                new_source = source.replace("process_file(local_file,model_name)", "await process_file(local_file,model_name)")
                cell['source'] = [line + '\n' for line in new_source.split('\n') if line]

    with open(filepath, 'w') as f:
        json.dump(nb, f, indent=2)

print("Async notebooks fixed successfully!")
