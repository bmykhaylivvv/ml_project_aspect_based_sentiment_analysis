def get_corefs(ann):
    corefs = {}
    unresolved_mentions = set()
    min_indexes = set()
    for coref in ann.corefChain:
        mentions = []
        min_sentenceIndex = float("inf")
        min_headIndex = float("inf")
        for mention in coref.mention:
            if mention.sentenceIndex == min_sentenceIndex:
                if mention.headIndex < min_headIndex:
                    min_headIndex = mention.headIndex
            if mention.sentenceIndex < min_sentenceIndex:
                min_sentenceIndex = mention.sentenceIndex
                min_headIndex = mention.headIndex

            mentions.append((mention.sentenceIndex, mention.headIndex + 1))
        min_indexes.add((min_sentenceIndex, min_headIndex + 1))
        if len(mentions) > 1:
            for mention in mentions:
                key = mention[0], mention[1]
                value = [m for m in mentions if m != mention]
                corefs[key] = value
        else:
            if len(mentions) == 1:
                ### add pronouns to unresolved
                if ann.sentence[mentions[0][0]].token[mentions[0][1]-1].pos == "PRP":
                    unresolved_mentions.add(mentions[0])

    corefs_pivot = {}
    for key in corefs:
        if key in min_indexes:
            replacable_words = corefs[key]
            ### add pronouns to unresolved
            if ann.sentence[key[0]].token[key[1]-1].pos == "PRP":
                unresolved_mentions.add(key)
                for replacable_word in replacable_words:
                    unresolved_mentions.add(replacable_word)
            ##############################
            for replacable_word in replacable_words:
                corefs_pivot[replacable_word] = key

    return corefs_pivot, unresolved_mentions


if __name__ == "__main__":
    pass
