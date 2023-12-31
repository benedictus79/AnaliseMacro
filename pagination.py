from login import analisemacrosession


def pagination(data_pager_results_json, course_id):
  params = {
    'action': [
      'ld30_ajax_pager',
      'ld30_ajax_pager',
    ],
    'ld-courseinfo-lesson-page': data_pager_results_json['paged'],
    'pager_nonce': data_pager_results_json['nonce'],
    'pager_results%5Bpaged%5D': data_pager_results_json['paged'],
    'pager_results%5Btotal_items%5D': data_pager_results_json['total_items'],
    'pager_results%5Btotal_pages%5D': data_pager_results_json['total_pages'],
    'context': 'course_content_shortcode',
    'course_id': course_id,
    'shortcode_instance%5Bcourse_id%5D': course_id,
    'shortcode_instance%5Bpost_id%5D': course_id,
    'shortcode_instance%5Bgroup_id%5D': '0',
    'shortcode_instance%5Bpaged%5D': '1',
    'shortcode_instance%5Bnum%5D': data_pager_results_json['total_items'],
    'shortcode_instance%5Bwrapper%5D': 'true',
    'pager_results[paged]': data_pager_results_json['paged'],
    'pager_results[total_items]': data_pager_results_json['total_items'],
    'pager_results[total_pages]': data_pager_results_json['total_pages'],
    'shortcode_instance[course_id]': course_id,
    'shortcode_instance[post_id]': course_id,
    'shortcode_instance[group_id]': '0',
    'shortcode_instance[paged]': data_pager_results_json['paged'],
    'shortcode_instance[num]': data_pager_results_json['total_items'],
    'shortcode_instance[wrapper]': 'false',
  }
  response = analisemacrosession.get(
    'https://aluno.analisemacro.com.br/wp-admin/admin-ajax.php',
    params=params,
    cookies=analisemacrosession.cookies,
    headers=analisemacrosession.headers,
  )

  return response.json()['data']['markup']
