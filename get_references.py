import re
import sys

import yaml

myrefs = dict()
pattern = re.escape("\\cite{")  + "([\w,\s]*)" + re.escape("}")
# pattern = re.escape("\\cite{")  + "(.*)" + re.escape("}")

def main(tex_files):

    for tex in tex_files:

        with open(tex) as tex_file:
            text = tex_file.read().replace('\n', '')

            refs_raw = re.findall(pattern,text)
            for refs_i in refs_raw:
                refs = refs_i.split(',')
                for r in refs:
                    myrefs[r.strip()] = 1


    print(myrefs)

    with open('data.yml', 'w') as outfile:
        yaml.dump(myrefs, outfile, default_flow_style=False)


if __name__ == '__main__':

    main(sys.argv[1:])
