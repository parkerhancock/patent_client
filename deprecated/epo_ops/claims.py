Claim = namedtuple("Claim", ["number", "text", "limitations"])
cn_re = re.compile(r"^\d+")
lim_re = re.compile(r"([:;])")


def clean_claims(claims):
    def parse_claim(limitations, counter):
        preamble = limitations[0]
        claim_number = counter
        if preamble[0].isupper():
            limitations = [f"{str(claim_number)}. {preamble}", *limitations[1:]]
            counter += 1
        elif cn_re.search(preamble):
            claim_number = int(cn_re.search(preamble).group(0))
            counter = claim_number + 1

        # Fix trailing "ands" in the claim language
        clean_limitations = list()
        for i, lim in enumerate(limitations):
            try:
                if limitations[i + 1].split()[0].lower() == "and":
                    lim = lim + " and"
                    limitations[i + 1] = " ".join(limitations[i + 1].split()[1:])
            except IndexError:
                pass
            clean_limitations.append(lim.strip())
        return (
            Claim(
                number=claim_number,
                text="\n".join(clean_limitations),
                limitations=clean_limitations,
            ),
            counter,
        )

    if len(claims) > 1:
        counter = 1
        claim_list = list()
        for claim in claims:
            segments = iter(lim_re.split(claim))
            limitations = list()
            while True:
                try:
                    phrase = next(segments)
                    delimiter = next(segments)
                    limitations.append(phrase + delimiter)
                except StopIteration:
                    limitations.append(phrase)
                    break
            claim, counter = parse_claim(limitations, counter)
            claim_list.append(claim)
        return claim_list

    lines = claims[0].split("\n")

    preambles = ["i claim", "we claim", "what is claimed", "claims"]
    c_preambles = ["a", "an", "the"]

    if any(pa in lines[0].lower().replace(" ", "") for pa in preambles):
        lines = lines[1:]

    new_lines = list()

    for line in lines:
        segments = re.split(r"(?<=[^\d]\.) ", line)
        new_lines += segments

    claims = list()
    counter = 1
    limitations = list()
    while new_lines:
        line = new_lines.pop(0)
        if limitations and (
            any(cp in line[0].split()[0].lower() for cp in c_preambles)
            or cn_re.search(line)
            or not new_lines
        ):
            claim, counter = parse_claim(limitations, counter)
            claims.append(claim)
            limitations = [line]
        else:
            limitations.append(line)

    claim, counter = parse_claim(limitations, counter)
    claims.append(claim)
    return claims