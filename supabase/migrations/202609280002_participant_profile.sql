alter table public.participants
  add column full_name text,
  add column participant_role text,
  add column class_group text,
  add column age_group text,
  add column gender text,
  add constraint participants_full_name_check check (
    full_name is null or char_length(btrim(full_name)) between 2 and 120
  ),
  add constraint participants_role_check check (
    participant_role is null or participant_role in ('Aluno', 'Professor', 'Responsável', 'Convidado')
  ),
  add constraint participants_class_group_check check (
    class_group is null or char_length(btrim(class_group)) between 1 and 40
  ),
  add constraint participants_age_group_check check (
    age_group is null or age_group in ('Até 10', '11–14', '15–17', '18–24', '25–39', '40+', 'Prefiro não responder')
  ),
  add constraint participants_gender_check check (
    gender is null or gender in ('Mulher', 'Homem', 'Não binário', 'Outro', 'Prefiro não responder')
  ),
  add constraint participants_profile_completion_check check (
    (
      full_name is null
      and participant_role is null
      and class_group is null
      and age_group is null
      and gender is null
    )
    or (
      full_name is not null
      and participant_role is not null
      and age_group is not null
      and gender is not null
      and (
        (participant_role = 'Aluno' and class_group is not null)
        or (participant_role <> 'Aluno' and class_group is null)
      )
    )
  );

comment on column public.participants.full_name is
  'Required participant profile field collected once after account login.';
comment on column public.participants.participant_role is
  'Participant profile: student, teacher, guardian, or guest.';