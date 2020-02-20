from boolean_search.request_parser import Parser


def build_index(file_name):
    reverse_index = {}
    with open(file_name, 'r') as file:
        for cur_line in file.readlines():
            parts = cur_line.split()
            doc_id = int(parts[0])
            words = parts[1:]
            for cur_word in words:
                cur_word = cur_word.upper()
                if cur_word not in reverse_index:
                    reverse_index[cur_word] = set()
                reverse_index[cur_word].add(doc_id)
    return reverse_index


def get_queries(file_name):
    queries = []
    with open(file_name, 'r') as file:
        for cur_line in file.readlines():
            query_string = cur_line.split('\t')
            parser = Parser(query_string[1])
            queries.append(parser.parse())
    return queries


def get_objects_to_answer(file_name):
    with open(file_name, 'r') as file:
        file.readline()
        for cur_line in file.readlines():
            object_id, query_id, document_id = cur_line.split(',')
            yield object_id, int(query_id) - 1, int(document_id)


def print_answers(responses, answers_file_name, questions_file_name):
    with open(answers_file_name, 'w') as file:
        file.write("ObjectId,Relevance\n")
        for object_id, query_id, document_id in get_objects_to_answer(questions_file_name):
            if document_id in responses[query_id]:
                file.write(object_id + ",1\n")
            else:
                file.write(object_id + ",0\n")


def main():
    reverse_index = build_index("data/docs.tsv")
    queries = get_queries("data/queries.numerate.txt")
    responses = [query.get_documents(reverse_index) for query in queries]
    print_answers(responses, "data/result.txt", "data/objects.numerate.txt")


if __name__ == "__main__":
    main()
