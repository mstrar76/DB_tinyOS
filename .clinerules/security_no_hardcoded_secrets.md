# Regra: Gerenciamento Aprimorado de Segredos (Não Hardcodar)

## Instrução
É mandatório não 'hardcodar' segredos (chaves de API, senhas de banco de dados, tokens de autenticação, etc.) diretamente no código-fonte ou em arquivos de configuração que são versionados no Git.
Utilizar arquivos `.env` (devidamente listados no `.gitignore`) para desenvolvimento local.
Para ambientes de staging e produção, utilizar variáveis de ambiente injetadas pela plataforma de hospedagem ou por um sistema de gerenciamento de segredos.
O arquivo `tiny_token.json` e similares devem estar no `.gitignore`.

## Raciocínio
Previne a exposição acidental de credenciais sensíveis através do repositório de código, o que é uma vulnerabilidade de segurança grave. Separa a configuração do código, facilitando o gerenciamento de diferentes ambientes.
