-- Questões adicionais para o quiz EcoWatt.
-- Execute no Supabase SQL Editor depois das migrations do quiz.
-- Idempotente: IDs já existentes não são sobrescritos nem republicados.
-- Este script não altera event_quizzes.enabled.

begin;

insert into public.quiz_questions (
  id,
  quiz_id,
  prompt,
  explanation,
  options,
  correct_option,
  status
) values
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a101',
    '11111111-1111-4111-8111-111111111111',
    'Um chuveiro de 5.500 W é usado por 10 minutos ao dia durante 30 dias. Qual é o consumo aproximado no mês?',
    '5.500 W equivalem a 5,5 kW. Em 10 minutos, o consumo diário é 5,5 × 1/6 = 0,9167 kWh. Em 30 dias, são aproximadamente 27,5 kWh.',
    '["27,5 kWh", "5,5 kWh", "55 kWh"]'::jsonb,
    0,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a102',
    '11111111-1111-4111-8111-111111111111',
    'Uma lâmpada LED de 10 W fica acesa 5 horas por dia durante 30 dias. Qual é seu consumo mensal?',
    '10 W × 5 horas × 30 dias = 1.500 Wh, ou 1,5 kWh. Para converter Wh em kWh, dividimos por 1.000.',
    '["15 kWh", "1,5 kWh", "150 kWh"]'::jsonb,
    1,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a103',
    '11111111-1111-4111-8111-111111111111',
    'Qual aparelho consome mais energia nesse período: um de 100 W usado por 5 horas ou um de 200 W usado por 2 horas?',
    'O primeiro consome 100 W × 5 h = 500 Wh. O segundo consome 200 W × 2 h = 400 Wh. A potência sozinha não determina o consumo: o tempo de uso também conta.',
    '["O aparelho de 100 W", "O aparelho de 200 W", "Os dois consomem a mesma energia"]'::jsonb,
    0,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a104',
    '11111111-1111-4111-8111-111111111111',
    'Uma casa consumiu 120 kWh e a tarifa é R$ 0,85 por kWh. Qual é o custo de energia estimado, sem taxas adicionais?',
    'Multiplicamos o consumo pela tarifa: 120 kWh × R$ 0,85/kWh = R$ 102,00. Uma conta real pode incluir impostos, bandeiras e cobranças adicionais.',
    '["R$ 14,40", "R$ 102,00", "R$ 1.020,00"]'::jsonb,
    1,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a105',
    '11111111-1111-4111-8111-111111111111',
    'Dois aparelhos têm a mesma potência. Como comparar qual consumirá mais energia?',
    'Mantendo a mesma potência, o aparelho usado por mais tempo consome mais energia. Em geral, consumo depende da potência e do tempo de uso.',
    '["Pelo tempo de uso de cada um", "Pelo tamanho físico dos aparelhos", "Somente pela cor da etiqueta"]'::jsonb,
    0,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a106',
    '11111111-1111-4111-8111-111111111111',
    'Ao substituir uma lâmpada incandescente de 60 W por uma LED de 9 W, mantendo o mesmo tempo de uso, o que acontece?',
    'A lâmpada LED fornece iluminação semelhante com menor potência. Para 5 horas diárias por 30 dias, a diferença de 51 W representa cerca de 7,65 kWh economizados no mês.',
    '["O consumo da iluminação diminui", "O consumo dobra", "A troca não altera o consumo"]'::jsonb,
    0,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a107',
    '11111111-1111-4111-8111-111111111111',
    'Qual hábito ajuda a geladeira a trabalhar com menos desperdício de energia?',
    'Abrir a porta por menos tempo e evitar colocar alimentos ainda quentes reduz a entrada de calor e o trabalho do sistema de refrigeração.',
    '["Deixar a porta aberta para circular ar", "Guardar alimentos ainda quentes", "Abrir a porta pelo menor tempo possível"]'::jsonb,
    2,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a108',
    '11111111-1111-4111-8111-111111111111',
    'Em um dia quente, qual conjunto de ações pode ajudar a reduzir o consumo do ar-condicionado?',
    'Manter portas e janelas fechadas enquanto o aparelho funciona e escolher uma temperatura confortável reduz a entrada de calor e evita esforço desnecessário.',
    '["Manter janelas abertas e escolher a menor temperatura", "Fechar portas e janelas e usar uma temperatura confortável", "Ligar e desligar o aparelho a cada minuto"]'::jsonb,
    1,
    'published'
  ),
  (
    '51f7c43e-135c-4a62-9601-5583d9d8a109',
    '11111111-1111-4111-8111-111111111111',
    'O selo de eficiência energética ajuda principalmente a comparar o quê?',
    'O selo informa a eficiência energética do produto dentro de categorias comparáveis. A comparação deve considerar aparelhos de tipo e capacidade semelhantes.',
    '["A eficiência energética entre produtos comparáveis", "O preço futuro da conta de luz", "A quantidade de horas que cada pessoa usará o aparelho"]'::jsonb,
    0,
    'published'
  )
on conflict (id) do nothing;

commit;

-- Conferência: o quiz deve retornar 12 perguntas publicadas após este script.
select
  q.event_key,
  q.enabled,
  count(qq.id) filter (where qq.status = 'published') as published_questions
from public.event_quizzes q
left join public.quiz_questions qq on qq.quiz_id = q.id
where q.id = '11111111-1111-4111-8111-111111111111'
group by q.event_key, q.enabled;
