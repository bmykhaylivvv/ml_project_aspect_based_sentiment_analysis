from coref_resolution import get_corefs
from stanza.server import CoreNLPClient


def get_word(ann, sentenceIndex, tokenIndex):
    return ann.sentence[sentenceIndex].token[tokenIndex].word


def join_compounds(ann):
    compound_main_words = dict()
    num_of_sentences = len(ann.sentence)
    for sentenceIndex in range(num_of_sentences):
        compound_ties = dict()
        compound_headIndexes = []
        sentence = ann.sentence[sentenceIndex]
        for dependencie in sentence.basicDependencies.edge:
            if dependencie.dep == 'compound':
                ### if we already had that gov word
                if dependencie.source in compound_ties:
                    if (abs(dependencie.source - dependencie.target) < abs(dependencie.source - compound_ties[dependencie.source])):
                        compound_headIndexes.remove(compound_ties[dependencie.source])
                        compound_ties[dependencie.source] = dependencie.target
                        compound_headIndexes.append(dependencie.target)
                    continue
                compound_ties[dependencie.source] = dependencie.target
                compound_headIndexes.append(dependencie.target)
                compound_headIndexes.append(dependencie.source)

        compound_headIndexes.sort()
        compound_chain = False
        while True:
            if len(compound_headIndexes) == 0:
                break
            if compound_chain == False:
                compound_headIndex = max(compound_headIndexes)
                main_compound_index = compound_headIndex
                compound_main_words[(sentenceIndex, main_compound_index)] = [get_word(ann, sentenceIndex, main_compound_index-1)]
                compound_headIndexes.remove(compound_headIndex)
                compound_chain = True
            else:
                if compound_headIndex in compound_ties:
                    compound_headIndex = compound_ties[compound_headIndex]
                    compound_headIndexes.remove(compound_headIndex)
                    compound_main_words[(sentenceIndex, main_compound_index)].append(get_word(ann, sentenceIndex, compound_headIndex-1))
                else:
                    compound_chain = False


    final_compounds = dict()
    for main_compound_key in compound_main_words:
        reversed_words = compound_main_words[main_compound_key]
        n = len(reversed_words)
        words = [0]*n
        for i in range(n):
            words[i] = reversed_words[n-i-1]
        final_compounds[main_compound_key] = "-".join(words)

    return final_compounds


def join_xcomp_advmod(ann):
    advmods = dict()
    xcomps = dict()
    num_of_sentences = len(ann.sentence)
    for sentenceIndex in range(num_of_sentences):
        sentence = ann.sentence[sentenceIndex]
        for dependencie in sentence.basicDependencies.edge:
            if dependencie.dep == 'advmod':
                if not (get_word(ann, sentenceIndex, dependencie.target-1) == "WRB"):
                    advmods[(sentenceIndex, dependencie.source)] = (sentenceIndex, dependencie.target)
            if dependencie.dep == 'xcomp':
                xcomps[(sentenceIndex, dependencie.source)] = (sentenceIndex, dependencie.target)

    xcomps_advmods = dict()
    for gov in advmods:
        dependent = advmods[gov]
        gov_word = get_word(ann, gov[0], gov[1]-1)
        dep_word = get_word(ann, dependent[0], dependent[1]-1)
        if dependent[1] > gov[1]:
            xcomps_advmods[gov] = f"{gov_word}-{dep_word}"
        else:
            xcomps_advmods[gov] = f"{dep_word}-{gov_word}"

    for gov in xcomps:
        dependent = xcomps[gov]
        gov_word = get_word(ann, gov[0], gov[1]-1)
        dependent_word = get_word(ann, dependent[0], dependent[1]-1)
        if dependent in xcomps_advmods:
            dependent_word = xcomps_advmods[dependent]

        xcomps_advmods[gov] = f"{gov_word}-{dependent_word}"

    return xcomps_advmods


def replace_with_corefs(ann, opinion_pairs, corefs_pivot):
    n = len(opinion_pairs)
    for i in range(n):
        opinion_pair = opinion_pairs[i]
        dependencie_type = opinion_pair[0]
        new_governor = opinion_pair[1]
        new_dependent = opinion_pair[2]
        if opinion_pair[1][1] in corefs_pivot:
            new_governor_ind = corefs_pivot[opinion_pair[1][1]]
            new_governor = (ann.sentence[new_governor_ind[0]].token[new_governor_ind[1] - 1].word, new_governor_ind)

        if opinion_pair[2][1] in corefs_pivot:
            new_dependent_ind = corefs_pivot[opinion_pair[2][1]]
            new_dependent = (ann.sentence[new_dependent_ind[0]].token[new_dependent_ind[1] - 1].word, new_dependent_ind)

        opinion_pairs[i] = (dependencie_type,new_governor, new_dependent)


def replace_words_with_structure(opinion_pairs, structure_dict):
    n = len(opinion_pairs)
    for i in range(n):
        opinion_pair = opinion_pairs[i]
        dependencie_type = opinion_pair[0]
        new_governor = opinion_pair[1]
        new_dependent = opinion_pair[2]
        if opinion_pair[1][1] in structure_dict:
            new_governor_word = structure_dict[opinion_pair[1][1]]
            new_governor = (new_governor_word, opinion_pair[1][1])

        if opinion_pair[2][1] in structure_dict:
            new_dependent_word = structure_dict[opinion_pair[2][1]]
            new_dependent = (new_dependent_word, opinion_pair[2][1])

        opinion_pairs[i] = (dependencie_type ,new_governor, new_dependent)


def substract_opinion_pairs(ann, dependencies, unresolved_mentions):
    opinion_pairs = []
    for dependencie in dependencies:
        if ((dependencie[0] == 'nsubj') and (dependencie[2][1] not in unresolved_mentions) and (ann.sentence[dependencie[1][1][0]].token[dependencie[1][1][1]-1].sentiment != "Neutral")):
            opinion_pairs.append(dependencie)
        elif ((dependencie[0] == 'amod') and (ann.sentence[dependencie[1][1][0]].token[dependencie[2][1][1]-1].pos == "JJ")):
            opinion_pairs.append(dependencie)
        elif ((dependencie[0] == 'obj') and (ann.sentence[dependencie[1][1][0]].token[dependencie[1][1][1]-1].sentiment != "Neutral")):   ### ??????
            opinion_pairs.append(dependencie)
        else:
            continue
    return opinion_pairs


def extract_dependencies(ann):
    dependencies = []
    num_of_sentences = len(ann.sentence)
    for sentenceIndex in range(num_of_sentences):
        sentence = ann.sentence[sentenceIndex]
        for dependencie in sentence.basicDependencies.edge:
            governor = (sentenceIndex, dependencie.source)
            relation_type = dependencie.dep
            dependent = (sentenceIndex, dependencie.target)
            # One dependencie: ('obj', ('enjoyed', (0, 2)), ('resolution', (0, 5)))
            dependencies.append((relation_type, (sentence.token[governor[1]-1].word, governor), (sentence.token[dependent[1]-1].word, dependent)))
    return dependencies


def create_aspects_dict(opinion_pairs):
    aspects_dict = dict()    # {aspect: [sentiment_word1, ....]}
    for opinion_pair in opinion_pairs:
        aspect = opinion_pair[2]
        sentiment_word = opinion_pair[1]
        if (opinion_pair[0] == 'nsubj'):
            aspect = opinion_pair[2]
            sentiment_word = opinion_pair[1]
        elif (opinion_pair[0] == 'amod'):
            aspect = opinion_pair[1]
            sentiment_word = opinion_pair[2]
        elif (opinion_pair[0] == 'obj'):
            aspect = opinion_pair[2]
            sentiment_word = opinion_pair[1]
        else:
            pass

        if aspect in aspects_dict:
            aspects_dict[aspect].append(sentiment_word)
        else:
            aspects_dict[aspect] = [sentiment_word]

    return aspects_dict


def print_apects_dict(aspects_dict):
    for aspect in aspects_dict:
        print(aspect[0], ': ', [sentiment_word[0] for sentiment_word in aspects_dict[aspect]], sep='')


def parse_text(text):
    ann = None
    # Set up the client
    with CoreNLPClient(be_quite=False, annotators=['tokenize', 'ssplit', 'pos', 'lemma', 'ner', 'parse', 'coref'], timeout=30000, memory='16G', endpoint='http://localhost:5003') as client:        
        # Parse the text using the client
        ann = client.annotate(text)

        client.stop()
    return ann


def get_pairs_dict(ann):
    compounds = join_compounds(ann)
    xcomps_advmods = join_xcomp_advmod(ann)

    # Extract the set of grammar dependencies
    # One dependencie: ('obj', ('enjoyed', (0, 2)), ('resolution', (0, 5)))
    dependencies = extract_dependencies(ann)

    # Unresolved mentions: {(0, 1), (2, 3)}
    # Corefs: {(2, 3): (0, 1), (1, 1): (0, 5), (0, 7): (0, 5)}
    corefs_pivot, unresolved_mentions = get_corefs(ann)

    # One opinion pair: ('obj', ('enjoyed', (0, 2)), ('resolution', (0, 5)))
    opinion_pairs = substract_opinion_pairs(ann, dependencies, unresolved_mentions)

    # Replace words with their coreferences
    replace_with_corefs(ann, opinion_pairs, corefs_pivot)

    # Connecting compounds
    replace_words_with_structure(opinion_pairs, compounds)

    # Connecting xcomps and advmods
    replace_words_with_structure(opinion_pairs, xcomps_advmods)

    aspects_dict = create_aspects_dict(opinion_pairs)

    formatted_return = []
    for aspect in aspects_dict:
        name = aspect[0]
        tuples = aspects_dict[aspect]
        descriptions = [tup[0] for tup in tuples]
        formatted_return.append({"name": name, "descriptions": descriptions})

    return formatted_return


if __name__ == "__main__":
    pass
