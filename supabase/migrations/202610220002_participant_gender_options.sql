alter table public.participants drop constraint participants_gender_check;

-- Perfis com gênero que deixou de existir voltam a ser incompletos e são preenchidos de novo no próximo login.
update public.participants
set full_name = null, participant_role = null, class_group = null, age_group = null, gender = null
where gender is not null and gender not in ('Mulher', 'Homem');

update public.participants set gender = 'Feminino' where gender = 'Mulher';
update public.participants set gender = 'Masculino' where gender = 'Homem';

alter table public.participants
  add constraint participants_gender_check check (
    gender is null or gender in ('Feminino', 'Masculino')
  );
