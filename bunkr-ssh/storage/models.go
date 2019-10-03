package storage

type Secret struct {
	Name       string
	FileId     string
	CapId      string
	SecretType string
	PublicData []byte
	Group      *Secret
}
