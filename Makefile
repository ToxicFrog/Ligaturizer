TTF_SRCS=$(wildcard input-fonts/*.ttf)
OTF_SRCS=$(wildcard input-fonts/*.otf)

TTF_OUTS=$(patsubst input-fonts/%,output-fonts/Liga%,${TTF_SRCS})
OTF_OUTS=$(patsubst input-fonts/%.otf,output-fonts/Liga%.ttf,${OTF_SRCS})

all: ${TTF_OUTS} ${OTF_OUTS}

output-fonts/Liga%.ttf: input-fonts/%.* ligatures.py ligaturize.py
	fontforge -lang=py ligaturize.py "$<" "$@"
