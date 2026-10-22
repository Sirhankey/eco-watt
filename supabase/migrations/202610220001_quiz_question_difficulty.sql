alter table public.quiz_questions
  add column if not exists difficulty text not null default 'medium'
  check (difficulty in ('easy', 'medium', 'hard'));

update public.quiz_questions set difficulty = 'easy' where id in (
  '22222222-2222-4222-8222-222222222221',
  '22222222-2222-4222-8222-222222222222',
  '22222222-2222-4222-8222-222222222223',
  '51f7c43e-135c-4a62-9601-5583d9d8a104',
  '51f7c43e-135c-4a62-9601-5583d9d8a105',
  '51f7c43e-135c-4a62-9601-5583d9d8a107',
  '51f7c43e-135c-4a62-9601-5583d9d8a108',
  'c09b3dc3-35f4-4088-bdee-1dcfdef50e08',
  '0dc408c2-3db3-4bb4-ae5b-4deb1b1d9865',
  '3305033d-4ec5-4c42-be32-154d08a9efd8',
  '2e8971a5-6924-48bc-baf0-e2c6a911e40f',
  '4eb8c200-5310-4085-b048-877600297bf9',
  '816e89a8-9ac4-4303-9684-8be354d7cdd6',
  '2d3a37f5-5eb4-413c-88ac-56d87cd4007c',
  '08e6671a-944f-46e2-b5bd-8b004feb0676',
  '9a294921-7009-40df-97a5-58da9fed3b7f',
  '54f2e5b5-a16d-4cb0-9489-d18742af2df0'
);

update public.quiz_questions set difficulty = 'medium' where id in (
  '51f7c43e-135c-4a62-9601-5583d9d8a102',
  '51f7c43e-135c-4a62-9601-5583d9d8a106',
  '51f7c43e-135c-4a62-9601-5583d9d8a109',
  '72699853-891d-47ef-b991-1c51bda6aab7',
  '4d9e3c39-fedb-4ff1-b4d2-cbd5a11dbc96',
  '6a92aa57-4d39-4d9a-874b-910d8b76009b',
  'a9ddf6d2-5ad6-4d46-b22d-d37d24669c84',
  '2ffddd68-fd43-4a17-b878-954da1bbc3f1',
  'c08a1703-d492-49d1-9d2f-5a691d1fd3e6',
  'ca28d56c-24fb-4462-8420-d057a3250540'
);

update public.quiz_questions set difficulty = 'hard' where id in (
  '51f7c43e-135c-4a62-9601-5583d9d8a101',
  '51f7c43e-135c-4a62-9601-5583d9d8a103',
  'bf16cc73-9cb3-45f1-a33d-bb1dcc65f9f0',
  'bfdc2c6e-cc26-496e-b6fe-9b6b4f96e578',
  'aa014561-08ad-43ee-af06-1d93c69c501c'
);
