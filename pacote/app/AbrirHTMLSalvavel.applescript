-- App "Abrir HTML Salvável": pergunta qual projeto abrir (lista dos últimos), lembra a escolha
-- e liga o servidor do HTML salvável naquela pasta (uma janela do Terminal fica aberta enquanto você testa).
set base to (POSIX path of (path to home folder)) & "Ferramentas/html-salvavel/"
set memoria to base & "ultimos-projetos.txt"
set antiga to base & "ultima-pasta.txt"
set titulo to "Abrir HTML salvável"
set maximo to 8

-- Últimos projetos (o mais recente primeiro), sem pastas que não existem mais.
set linhas to {}
try
	set linhas to paragraphs of (do shell script "cat " & quoted form of memoria & " 2>/dev/null || cat " & quoted form of antiga & " 2>/dev/null || true")
end try
set recentes to {}
repeat with l in linhas
	set l to contents of l
	if l is not "" and recentes does not contain l then
		if (do shell script "test -d " & quoted form of l & " && echo s || echo n") is "s" then set end of recentes to l
	end if
end repeat

-- Nome que aparece na lista: "Pasta  (pasta-mãe)", para diferenciar projetos com nomes parecidos.
on rotulo(caminho)
	set n to do shell script "basename " & quoted form of caminho
	set m to do shell script "basename \"$(dirname " & quoted form of caminho & ")\""
	return n & "   (" & m & ")"
end rotulo

set outra to "📁 Outra pasta…"
set pasta to ""
if (count of recentes) > 0 then
	set opcoes to {}
	repeat with r in recentes
		set end of opcoes to rotulo(contents of r)
	end repeat
	set end of opcoes to outra
	set escolha to choose from list opcoes with title titulo with prompt "Qual projeto você quer abrir?" default items {item 1 of opcoes} OK button name "Abrir" cancel button name "Cancelar"
	if escolha is false then return
	set escolha to item 1 of escolha
	if escolha is not outra then
		repeat with i from 1 to count of recentes
			if item i of opcoes is escolha then set pasta to item i of recentes
		end repeat
	end if
end if

-- Onde a janela de escolher pasta começa: ao lado do último projeto, senão na pasta pessoal.
set inicio to POSIX path of (path to home folder)
if (count of recentes) > 0 then set inicio to do shell script "dirname " & quoted form of (item 1 of recentes)
if pasta is "" and (count of recentes) is 0 then
	display dialog "Na próxima janela, escolha a pasta do projeto que tem o HTML de teste." & return & return & "Da próxima vez ela aparece na lista dos últimos projetos." buttons {"Cancelar", "Escolher pasta…"} default button 2 cancel button 1 with title titulo with icon note
end if

repeat while pasta is ""
	set p to POSIX path of (choose folder with prompt "Escolha a pasta do projeto, onde está o HTML de teste:" default location (POSIX file inicio as alias))
	if p ends with "/" and (length of p) > 1 then set p to text 1 thru -2 of p
	set n to do shell script "grep -l 'id=\"dados-salvos\"' " & quoted form of p & "/*.html 2>/dev/null | wc -l | tr -d ' '"
	if n is "0" then
		display dialog "Essa pasta ainda não tem HTML de teste." & return & return & "Para criar: abra o Claude Code nessa pasta e digite /roteiro-de-teste. Depois, abra por aqui." buttons {"Cancelar", "Escolher outra"} default button 2 cancel button 1 with title titulo with icon caution
	else
		set pasta to p
	end if
end repeat

-- Põe a escolhida no topo da lista e guarda as últimas.
set novos to {pasta}
repeat with r in recentes
	if (contents of r) is not pasta and (count of novos) < maximo then set end of novos to contents of r
end repeat
set AppleScript's text item delimiters to linefeed
set texto to novos as text
set AppleScript's text item delimiters to ""
do shell script "printf '%s\\n' " & quoted form of texto & " > " & quoted form of memoria & " && rm -f " & quoted form of antiga

tell application "Terminal"
	activate
	do script quoted form of (base & "abrir-pasta.sh") & " " & quoted form of pasta
end tell
