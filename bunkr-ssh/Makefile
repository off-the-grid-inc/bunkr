.PHONY: all clean bunkr-ssh

all: bunkr-ssh

clean:
	@echo "Deleting Bunkr SSH-Agent..."
	@rm -f bin/bunkr-ssh

bunkr-ssh:
	@echo "Building Bunkr SSH-Agent..."
	@go build \
	-ldflags " \
	-X main.Version=`cat .git/refs/heads/master` \
	" \
	-o bin/bunkr-ssh github.com/off-the-grid-inc/bunkr/ssh-agent/cmd
