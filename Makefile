TTF_SRCS=$(wildcard input-fonts/*.ttf)
OTF_SRCS=$(wildcard input-fonts/*.otf)

TTF_OUTS=$(patsubst input-fonts/%,output-fonts/%,${TTF_SRCS})
OTF_OUTS=$(patsubst input-fonts/%.otf,output-fonts/%.ttf,${OTF_SRCS})

all: ${TTF_OUTS} ${OTF_OUTS}

output-fonts/%.ttf: input-fonts/%.* ligatures.py ligaturize.py
	fontforge -lang=py ligaturize.py "$<" "$@"
